package storage

import (
	"bytes"
	"container/list"
	"crypto/sha1"
	"encoding/binary"
	"encoding/json"
	"encoding/xml"
	"errors"
	"fmt"
	"hash/fnv"
	"io"
	"os"
	"path/filepath"
	"sync"
	"time"

	"compress/zlib"
)

const (
	shardCount             = 10
	headerSize             = 8
	magic           uint16 = 0x4C42 // "LB"
	version         uint8  = 1
	statusActive           = byte(1)
	statusTombstone        = byte(2)
)

// JSONPayload REST girişinde beklenen veri formatını temsil eder.
type JSONPayload struct {
	Key  string            `json:"key"`
	Data map[string]any    `json:"data"`
	Meta map[string]string `json:"meta,omitempty"`
	Time time.Time         `json:"time,omitempty"`
}

// XMLNode map verisini XML'de hiyerarşik taşımak için düğümdür.
type XMLNode struct {
	XMLName xml.Name
	Value   string    `xml:",chardata"`
	Nodes   []XMLNode `xml:",any"`
}

// XMLPayload saklama öncesi XML'e serialize edilen veri modelidir.
type XMLPayload struct {
	XMLName xml.Name `xml:"record"`
	Key     string   `xml:"key"`
	Time    string   `xml:"time"`
	Data    XMLNode  `xml:"data"`
	Meta    XMLNode  `xml:"meta"`
}

// IndexEntry bir kaydın dosyadaki fiziksel konumunu tutar.
type IndexEntry struct {
	Offset         int64
	CompressedSize uint32
	RawSize        uint32
	Deleted        bool
}

type shard struct {
	id      int
	path    string
	walPath string
	mu      sync.RWMutex
	file    *os.File
	index   map[string]IndexEntry
}

// CacheItem LRU'daki cache elemanını taşır.
type CacheItem struct {
	Key string
	Val []byte
}

// LRUCache basit bir LRU cache implementasyonudur.
type LRUCache struct {
	cap   int
	mu    sync.Mutex
	ll    *list.List
	nodes map[string]*list.Element
}

func NewLRU(capacity int) *LRUCache {
	return &LRUCache{cap: capacity, ll: list.New(), nodes: make(map[string]*list.Element)}
}

func (c *LRUCache) Get(key string) ([]byte, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if ele, ok := c.nodes[key]; ok {
		c.ll.MoveToFront(ele)
		return ele.Value.(*CacheItem).Val, true
	}
	return nil, false
}

func (c *LRUCache) Set(key string, val []byte) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if ele, ok := c.nodes[key]; ok {
		ele.Value.(*CacheItem).Val = val
		c.ll.MoveToFront(ele)
		return
	}
	ele := c.ll.PushFront(&CacheItem{Key: key, Val: val})
	c.nodes[key] = ele
	if c.ll.Len() > c.cap {
		tail := c.ll.Back()
		if tail != nil {
			c.ll.Remove(tail)
			delete(c.nodes, tail.Value.(*CacheItem).Key)
		}
	}
}

func (c *LRUCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if ele, ok := c.nodes[key]; ok {
		c.ll.Remove(ele)
		delete(c.nodes, key)
	}
}

// Engine hibrit saklama motorunun ana yapısıdır.
type Engine struct {
	baseDir string
	shards  []*shard
	cache   *LRUCache
}

// ShardStat dashboard için shard bazlı metrikleri döner.
type ShardStat struct {
	ShardID          int     `json:"shard_id"`
	FileSize         int64   `json:"file_size"`
	RecordCount      int     `json:"record_count"`
	RawBytes         int64   `json:"raw_bytes"`
	CompressedBytes  int64   `json:"compressed_bytes"`
	CompressionRatio float64 `json:"compression_ratio"`
}

func NewEngine(baseDir string, cacheCap int) (*Engine, error) {
	if err := os.MkdirAll(baseDir, 0o755); err != nil {
		return nil, err
	}
	e := &Engine{baseDir: baseDir, cache: NewLRU(cacheCap)}
	for i := 0; i < shardCount; i++ {
		s := &shard{id: i, path: filepath.Join(baseDir, fmt.Sprintf("shard_%d.LIB", i)), walPath: filepath.Join(baseDir, fmt.Sprintf("shard_%d.wal", i)), index: map[string]IndexEntry{}}
		if err := s.openAndRecover(); err != nil {
			return nil, err
		}
		e.shards = append(e.shards, s)
	}
	return e, nil
}

func (s *shard) openAndRecover() error {
	f, err := os.OpenFile(s.path, os.O_RDWR|os.O_CREATE, 0o644)
	if err != nil {
		return err
	}
	s.file = f
	stat, err := f.Stat()
	if err != nil {
		return err
	}
	if stat.Size() < headerSize {
		if err := writeHeader(f, headerSize); err != nil {
			return err
		}
	}
	if err := s.rebuildIndex(); err != nil {
		return err
	}
	return s.replayWAL()
}

func writeHeader(f *os.File, indexOffset int64) error {
	header := packHeader(indexOffset)
	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, header)
	if _, err := f.WriteAt(buf, 0); err != nil {
		return err
	}
	return f.Sync()
}

func packHeader(indexOffset int64) uint64 {
	return (uint64(magic) << 48) | (uint64(version) << 40) | (uint64(indexOffset) & ((1 << 40) - 1))
}

func unpackHeader(v uint64) (uint16, uint8, int64) {
	m := uint16(v >> 48)
	ver := uint8((v >> 40) & 0xFF)
	off := int64(v & ((1 << 40) - 1))
	return m, ver, off
}

func (s *shard) rebuildIndex() error {
	s.index = map[string]IndexEntry{}
	if _, err := s.file.Seek(headerSize, io.SeekStart); err != nil {
		return err
	}
	offset := int64(headerSize)
	for {
		hdr := make([]byte, 11)
		_, err := io.ReadFull(s.file, hdr)
		if errors.Is(err, io.EOF) || errors.Is(err, io.ErrUnexpectedEOF) {
			break
		}
		if err != nil {
			return err
		}
		status := hdr[0]
		kLen := binary.BigEndian.Uint16(hdr[1:3])
		cSize := binary.BigEndian.Uint32(hdr[3:7])
		rSize := binary.BigEndian.Uint32(hdr[7:11])
		keyBuf := make([]byte, kLen)
		if _, err := io.ReadFull(s.file, keyBuf); err != nil {
			return err
		}
		if _, err := s.file.Seek(int64(cSize), io.SeekCurrent); err != nil {
			return err
		}
		key := string(keyBuf)
		s.index[key] = IndexEntry{Offset: offset, CompressedSize: cSize, RawSize: rSize, Deleted: status == statusTombstone}
		offset += int64(11) + int64(kLen) + int64(cSize)
	}
	return nil
}

func (s *shard) replayWAL() error {
	data, err := os.ReadFile(s.walPath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	if len(data) == 0 {
		return nil
	}
	// Basit WAL: tamamlanmamış intent varsa dosya sonundan rebuild ile güvenli duruma dönülür.
	if err := s.file.Sync(); err != nil {
		return err
	}
	if err := s.rebuildIndex(); err != nil {
		return err
	}
	return os.WriteFile(s.walPath, nil, 0o644)
}

func (e *Engine) shardFor(key string) *shard {
	h := fnv.New32a()
	_, _ = h.Write([]byte(key))
	return e.shards[h.Sum32()%shardCount]
}

func mapToNode(name string, m map[string]any) XMLNode {
	node := XMLNode{XMLName: xml.Name{Local: name}}
	for k, v := range m {
		switch vv := v.(type) {
		case map[string]any:
			node.Nodes = append(node.Nodes, mapToNode(k, vv))
		default:
			node.Nodes = append(node.Nodes, XMLNode{XMLName: xml.Name{Local: k}, Value: fmt.Sprintf("%v", vv)})
		}
	}
	return node
}

func metaToAny(meta map[string]string) map[string]any {
	out := make(map[string]any, len(meta))
	for k, v := range meta {
		out[k] = v
	}
	return out
}

func (e *Engine) encodePayload(p JSONPayload) ([]byte, []byte, error) {
	if p.Time.IsZero() {
		p.Time = time.Now().UTC()
	}
	x := XMLPayload{Key: p.Key, Time: p.Time.Format(time.RFC3339), Data: mapToNode("data", p.Data), Meta: mapToNode("meta", metaToAny(p.Meta))}
	raw, err := xml.MarshalIndent(x, "", "  ")
	if err != nil {
		return nil, nil, err
	}
	raw = append([]byte(xml.Header), raw...)
	var b bytes.Buffer
	zw, err := zlib.NewWriterLevel(&b, zlib.BestSpeed)
	if err != nil {
		return nil, nil, err
	}
	if _, err := zw.Write(raw); err != nil {
		return nil, nil, err
	}
	if err := zw.Close(); err != nil {
		return nil, nil, err
	}
	return raw, b.Bytes(), nil
}

func (e *Engine) walIntent(s *shard, key string, digest []byte) error {
	entry := map[string]any{"key": key, "digest": fmt.Sprintf("%x", digest), "time": time.Now().UTC().Format(time.RFC3339Nano)}
	b, _ := json.Marshal(entry)
	if err := os.WriteFile(s.walPath, b, 0o644); err != nil {
		return err
	}
	return nil
}

// Put JSON girdisini XML'e dönüştürüp sıkıştırarak shard'a atomik biçimde yazar.
func (e *Engine) Put(p JSONPayload) error {
	if p.Key == "" {
		return errors.New("key boş olamaz")
	}
	raw, cmp, err := e.encodePayload(p)
	if err != nil {
		return err
	}
	s := e.shardFor(p.Key)
	s.mu.Lock()
	defer s.mu.Unlock()

	digest := sha1.Sum(cmp)
	if err := e.walIntent(s, p.Key, digest[:]); err != nil {
		return err
	}
	off, err := s.file.Seek(0, io.SeekEnd)
	if err != nil {
		return err
	}
	rec := bytes.NewBuffer(nil)
	_ = rec.WriteByte(statusActive)
	_ = binary.Write(rec, binary.BigEndian, uint16(len(p.Key)))
	_ = binary.Write(rec, binary.BigEndian, uint32(len(cmp)))
	_ = binary.Write(rec, binary.BigEndian, uint32(len(raw)))
	rec.WriteString(p.Key)
	rec.Write(cmp)
	if _, err := s.file.Write(rec.Bytes()); err != nil {
		return err
	}
	if err := s.file.Sync(); err != nil {
		return err
	}
	s.index[p.Key] = IndexEntry{Offset: off, CompressedSize: uint32(len(cmp)), RawSize: uint32(len(raw))}
	if err := os.WriteFile(s.walPath, nil, 0o644); err != nil {
		return err
	}
	e.cache.Set(p.Key, raw)
	return nil
}

// Get key için XML verisini döndürür.
func (e *Engine) Get(key string) ([]byte, error) {
	if v, ok := e.cache.Get(key); ok {
		return v, nil
	}
	s := e.shardFor(key)
	s.mu.RLock()
	entry, ok := s.index[key]
	s.mu.RUnlock()
	if !ok || entry.Deleted {
		return nil, os.ErrNotExist
	}

	s.mu.RLock()
	defer s.mu.RUnlock()
	if _, err := s.file.Seek(entry.Offset, io.SeekStart); err != nil {
		return nil, err
	}
	hdr := make([]byte, 11)
	if _, err := io.ReadFull(s.file, hdr); err != nil {
		return nil, err
	}
	kLen := binary.BigEndian.Uint16(hdr[1:3])
	cSize := binary.BigEndian.Uint32(hdr[3:7])
	keyBuf := make([]byte, kLen)
	if _, err := io.ReadFull(s.file, keyBuf); err != nil {
		return nil, err
	}
	cmp := make([]byte, cSize)
	if _, err := io.ReadFull(s.file, cmp); err != nil {
		return nil, err
	}
	zr, err := zlib.NewReader(bytes.NewReader(cmp))
	if err != nil {
		return nil, err
	}
	defer zr.Close()
	raw, err := io.ReadAll(zr)
	if err != nil {
		return nil, err
	}
	e.cache.Set(key, raw)
	return raw, nil
}

// Delete kaydı tombstone olarak işaretler.
func (e *Engine) Delete(key string) error {
	s := e.shardFor(key)
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.index[key]; !ok {
		return os.ErrNotExist
	}
	off, _ := s.file.Seek(0, io.SeekEnd)
	rec := bytes.NewBuffer(nil)
	_ = rec.WriteByte(statusTombstone)
	_ = binary.Write(rec, binary.BigEndian, uint16(len(key)))
	_ = binary.Write(rec, binary.BigEndian, uint32(0))
	_ = binary.Write(rec, binary.BigEndian, uint32(0))
	rec.WriteString(key)
	if _, err := s.file.Write(rec.Bytes()); err != nil {
		return err
	}
	if err := s.file.Sync(); err != nil {
		return err
	}
	s.index[key] = IndexEntry{Offset: off, Deleted: true}
	e.cache.Delete(key)
	return nil
}

// Compact shard dosyalarını yeniden yazarak boşlukları temizler.
func (e *Engine) Compact() error {
	var wg sync.WaitGroup
	errCh := make(chan error, shardCount)
	for _, s := range e.shards {
		s := s
		wg.Add(1)
		go func() {
			defer wg.Done()
			s.mu.Lock()
			defer s.mu.Unlock()
			tmp := s.path + ".compact"
			nf, err := os.OpenFile(tmp, os.O_CREATE|os.O_RDWR|os.O_TRUNC, 0o644)
			if err != nil {
				errCh <- err
				return
			}
			if err := writeHeader(nf, headerSize); err != nil {
				errCh <- err
				return
			}
			newIndex := map[string]IndexEntry{}
			for key, entry := range s.index {
				if entry.Deleted {
					continue
				}
				if _, err := s.file.Seek(entry.Offset, io.SeekStart); err != nil {
					errCh <- err
					return
				}
				recLen := int64(11 + len(key) + int(entry.CompressedSize))
				buf := make([]byte, recLen)
				if _, err := io.ReadFull(s.file, buf); err != nil {
					errCh <- err
					return
				}
				off, _ := nf.Seek(0, io.SeekEnd)
				if _, err := nf.Write(buf); err != nil {
					errCh <- err
					return
				}
				newIndex[key] = IndexEntry{Offset: off, CompressedSize: entry.CompressedSize, RawSize: entry.RawSize}
			}
			if err := nf.Sync(); err != nil {
				errCh <- err
				return
			}
			if err := s.file.Close(); err != nil {
				errCh <- err
				return
			}
			if err := os.Rename(tmp, s.path); err != nil {
				errCh <- err
				return
			}
			f, err := os.OpenFile(s.path, os.O_RDWR, 0o644)
			if err != nil {
				errCh <- err
				return
			}
			s.file = f
			s.index = newIndex
		}()
	}
	wg.Wait()
	close(errCh)
	for err := range errCh {
		if err != nil {
			return err
		}
	}
	return nil
}

func (e *Engine) Stats() ([]ShardStat, error) {
	stats := make([]ShardStat, 0, shardCount)
	for _, s := range e.shards {
		s.mu.RLock()
		st, err := s.file.Stat()
		if err != nil {
			s.mu.RUnlock()
			return nil, err
		}
		var raw, comp int64
		count := 0
		for _, idx := range s.index {
			if idx.Deleted {
				continue
			}
			count++
			raw += int64(idx.RawSize)
			comp += int64(idx.CompressedSize)
		}
		s.mu.RUnlock()
		ratio := 1.0
		if raw > 0 {
			ratio = float64(comp) / float64(raw)
		}
		stats = append(stats, ShardStat{ShardID: s.id, FileSize: st.Size(), RecordCount: count, RawBytes: raw, CompressedBytes: comp, CompressionRatio: ratio})
	}
	return stats, nil
}

func (e *Engine) HeaderInfo(shardID int) (uint16, uint8, int64, error) {
	if shardID < 0 || shardID >= len(e.shards) {
		return 0, 0, 0, errors.New("invalid shard")
	}
	s := e.shards[shardID]
	s.mu.RLock()
	defer s.mu.RUnlock()
	buf := make([]byte, 8)
	if _, err := s.file.ReadAt(buf, 0); err != nil {
		return 0, 0, 0, err
	}
	m, v, off := unpackHeader(binary.BigEndian.Uint64(buf))
	return m, v, off, nil
}
