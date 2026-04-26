package main

import (
	"bufio"
	"bytes"
	"compress/zlib"
	"encoding/binary"
	"encoding/json"
	"encoding/xml"
	"errors"
	"fmt"
	"hash/crc32"
	"hash/fnv"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"
	"time"
)

const (
	shardCount        = 10
	headerSize        = 22
	libMagic   uint32 = 0x4C494230 // LIB0
	bagMagic   uint32 = 0x42414730 // BAG0
	version    uint16 = 1
)

type fileHeader struct {
	Magic      uint32
	Version    uint16
	EntryCount uint64
	LastOffset uint64
}

type libRecord struct {
	XMLName   xml.Name `xml:"record"`
	Key       string   `xml:"key"`
	Type      string   `xml:"type"`
	Size      uint64   `xml:"size"`
	BagOffset uint64   `xml:"bag_offset"`
	BagLength uint64   `xml:"bag_length"`
	CreatedAt string   `xml:"created_at"`
}

type shard struct {
	id int

	mu sync.Mutex

	libFile *os.File
	bagFile *os.File

	libWriter *bufio.Writer
	bagWriter *bufio.Writer

	libHeader fileHeader
	bagHeader fileHeader

	compressedBytes uint64
	rawBytes        uint64
	bytesWritten    uint64
	lastTickBytes   uint64
	ioBytesPerSec   uint64
}

type engine struct {
	baseDir string
	shards  [shardCount]*shard
	quit    chan struct{}
}

type putRequest struct {
	Key      string `json:"key"`
	DataType string `json:"data_type"`
	Data     string `json:"data"`
}

type putResponse struct {
	Shard     int    `json:"shard"`
	BagOffset uint64 `json:"bag_offset"`
	BagLength uint64 `json:"bag_length"`
}

type shardStats struct {
	ShardID             int     `json:"shard_id"`
	LibEntries          uint64  `json:"lib_entries"`
	BagEntries          uint64  `json:"bag_entries"`
	LibLastOffset       uint64  `json:"lib_last_offset"`
	BagLastOffset       uint64  `json:"bag_last_offset"`
	CompressionRatio    float64 `json:"compression_ratio"`
	IOBytesPerSecond    uint64  `json:"io_bytes_per_second"`
	LibFileSizeBytes    int64   `json:"lib_file_size_bytes"`
	BagFileSizeBytes    int64   `json:"bag_file_size_bytes"`
	EstimatedFillPctBag float64 `json:"estimated_fill_pct_bag"`
}

func main() {
	baseDir := os.Getenv("LIBBAG_DATA_DIR")
	if baseDir == "" {
		baseDir = "./data"
	}
	if err := os.MkdirAll(baseDir, 0o755); err != nil {
		log.Fatal(err)
	}

	eng, err := newEngine(baseDir)
	if err != nil {
		log.Fatal(err)
	}
	defer eng.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("/api/put", eng.handlePut)
	mux.HandleFunc("/api/stats", eng.handleStats)
	mux.Handle("/", http.FileServer(http.Dir("./")))

	addr := ":8080"
	log.Printf("LİB-BAG engine listening on %s, data dir: %s", addr, baseDir)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal(err)
	}
}

func newEngine(baseDir string) (*engine, error) {
	e := &engine{baseDir: baseDir, quit: make(chan struct{})}
	for i := 0; i < shardCount; i++ {
		s, err := openShard(baseDir, i)
		if err != nil {
			return nil, err
		}
		e.shards[i] = s
	}
	go e.metricsTicker()
	return e, nil
}

func (e *engine) Close() error {
	close(e.quit)
	var firstErr error
	for _, s := range e.shards {
		if s == nil {
			continue
		}
		s.mu.Lock()
		err := s.flushLocked()
		if err == nil {
			err = s.libFile.Close()
		}
		if err == nil {
			err = s.bagFile.Close()
		}
		s.mu.Unlock()
		if firstErr == nil && err != nil {
			firstErr = err
		}
	}
	return firstErr
}

func openShard(baseDir string, id int) (*shard, error) {
	libPath := filepath.Join(baseDir, fmt.Sprintf("node_%d.lib", id))
	bagPath := filepath.Join(baseDir, fmt.Sprintf("node_%d.bag", id))

	libFile, libHeader, err := openStorageFile(libPath, libMagic)
	if err != nil {
		return nil, err
	}
	bagFile, bagHeader, err := openStorageFile(bagPath, bagMagic)
	if err != nil {
		_ = libFile.Close()
		return nil, err
	}

	return &shard{
		id:        id,
		libFile:   libFile,
		bagFile:   bagFile,
		libWriter: bufio.NewWriterSize(libFile, 256*1024),
		bagWriter: bufio.NewWriterSize(bagFile, 1024*1024),
		libHeader: libHeader,
		bagHeader: bagHeader,
	}, nil
}

func openStorageFile(path string, magic uint32) (*os.File, fileHeader, error) {
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE, 0o644)
	if err != nil {
		return nil, fileHeader{}, err
	}
	st, err := f.Stat()
	if err != nil {
		_ = f.Close()
		return nil, fileHeader{}, err
	}
	if st.Size() == 0 {
		h := fileHeader{Magic: magic, Version: version, EntryCount: 0, LastOffset: headerSize}
		if err := writeHeader(f, h); err != nil {
			_ = f.Close()
			return nil, fileHeader{}, err
		}
		if _, err := f.Seek(headerSize, io.SeekStart); err != nil {
			_ = f.Close()
			return nil, fileHeader{}, err
		}
		return f, h, nil
	}
	h, err := readHeader(f)
	if err != nil {
		_ = f.Close()
		return nil, fileHeader{}, err
	}
	if h.Magic != magic {
		_ = f.Close()
		return nil, fileHeader{}, errors.New("invalid magic for file: " + path)
	}
	if _, err := f.Seek(int64(h.LastOffset), io.SeekStart); err != nil {
		_ = f.Close()
		return nil, fileHeader{}, err
	}
	return f, h, nil
}

func (e *engine) shardForKey(key string) *shard {
	h := fnv.New32a()
	_, _ = h.Write([]byte(key))
	idx := int(h.Sum32() % shardCount)
	return e.shards[idx]
}

func (e *engine) handlePut(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	defer r.Body.Close()
	var req putRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	if req.Key == "" {
		http.Error(w, "key required", http.StatusBadRequest)
		return
	}
	if req.DataType == "" {
		req.DataType = "binary"
	}
	payload := []byte(req.Data)
	s := e.shardForKey(req.Key)

	off, blen, err := s.append(req.Key, req.DataType, payload)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(putResponse{Shard: s.id, BagOffset: off, BagLength: blen})
}

func (e *engine) handleStats(w http.ResponseWriter, _ *http.Request) {
	stats := make([]shardStats, 0, shardCount)
	for _, s := range e.shards {
		s.mu.Lock()
		libStat, _ := s.libFile.Stat()
		bagStat, _ := s.bagFile.Stat()
		ratio := 1.0
		raw := atomic.LoadUint64(&s.rawBytes)
		cmp := atomic.LoadUint64(&s.compressedBytes)
		if raw > 0 {
			ratio = float64(cmp) / float64(raw)
		}
		bagSize := int64(0)
		if bagStat != nil {
			bagSize = bagStat.Size()
		}
		libSize := int64(0)
		if libStat != nil {
			libSize = libStat.Size()
		}
		fill := float64(0)
		if bagSize > 0 {
			fill = (float64(s.bagHeader.LastOffset) / float64(bagSize+1)) * 100
		}
		stats = append(stats, shardStats{
			ShardID:             s.id,
			LibEntries:          s.libHeader.EntryCount,
			BagEntries:          s.bagHeader.EntryCount,
			LibLastOffset:       s.libHeader.LastOffset,
			BagLastOffset:       s.bagHeader.LastOffset,
			CompressionRatio:    ratio,
			IOBytesPerSecond:    atomic.LoadUint64(&s.ioBytesPerSec),
			LibFileSizeBytes:    libSize,
			BagFileSizeBytes:    bagSize,
			EstimatedFillPctBag: fill,
		})
		s.mu.Unlock()
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(stats)
}

func (s *shard) append(key, dtype string, payload []byte) (uint64, uint64, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	bagOffset := s.bagHeader.LastOffset
	bagRecord, err := buildBagRecord(key, dtype, payload)
	if err != nil {
		return 0, 0, err
	}
	if _, err := s.bagWriter.Write(bagRecord); err != nil {
		return 0, 0, err
	}

	s.bagHeader.EntryCount++
	s.bagHeader.LastOffset += uint64(len(bagRecord))

	rec := libRecord{
		Key:       key,
		Type:      dtype,
		Size:      uint64(len(payload)),
		BagOffset: bagOffset,
		BagLength: uint64(len(bagRecord)),
		CreatedAt: time.Now().UTC().Format(time.RFC3339Nano),
	}
	xmlBytes, err := xml.Marshal(rec)
	if err != nil {
		return 0, 0, err
	}
	compressed, err := compressZlib(xmlBytes)
	if err != nil {
		return 0, 0, err
	}
	lenBuf := make([]byte, 4)
	binary.LittleEndian.PutUint32(lenBuf, uint32(len(compressed)))
	if _, err := s.libWriter.Write(lenBuf); err != nil {
		return 0, 0, err
	}
	if _, err := s.libWriter.Write(compressed); err != nil {
		return 0, 0, err
	}

	s.libHeader.EntryCount++
	s.libHeader.LastOffset += uint64(4 + len(compressed))
	atomic.AddUint64(&s.rawBytes, uint64(len(xmlBytes)))
	atomic.AddUint64(&s.compressedBytes, uint64(len(compressed)))
	atomic.AddUint64(&s.bytesWritten, uint64(len(compressed)+len(bagRecord)))

	if err := s.flushLocked(); err != nil {
		return 0, 0, err
	}
	return bagOffset, uint64(len(bagRecord)), nil
}

func (s *shard) flushLocked() error {
	if err := s.libWriter.Flush(); err != nil {
		return err
	}
	if err := s.bagWriter.Flush(); err != nil {
		return err
	}
	if err := writeHeader(s.libFile, s.libHeader); err != nil {
		return err
	}
	if err := writeHeader(s.bagFile, s.bagHeader); err != nil {
		return err
	}
	return nil
}

func buildBagRecord(key, dtype string, payload []byte) ([]byte, error) {
	if len(key) > 0xFFFF {
		return nil, errors.New("key too long")
	}
	buf := bytes.NewBuffer(make([]byte, 0, len(payload)+64))
	keyLen := uint16(len(key))
	if err := binary.Write(buf, binary.LittleEndian, keyLen); err != nil {
		return nil, err
	}
	if _, err := buf.Write([]byte(key)); err != nil {
		return nil, err
	}
	typeCode := byte(0)
	switch dtype {
	case "string":
		typeCode = 1
	case "xml":
		typeCode = 2
	default:
		typeCode = 0
	}
	if err := buf.WriteByte(typeCode); err != nil {
		return nil, err
	}
	payloadLen := uint64(len(payload))
	if err := binary.Write(buf, binary.LittleEndian, payloadLen); err != nil {
		return nil, err
	}
	if _, err := buf.Write(payload); err != nil {
		return nil, err
	}
	crc := crc32.ChecksumIEEE(payload)
	if err := binary.Write(buf, binary.LittleEndian, crc); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func compressZlib(src []byte) ([]byte, error) {
	var out bytes.Buffer
	w := zlib.NewWriter(&out)
	if _, err := w.Write(src); err != nil {
		_ = w.Close()
		return nil, err
	}
	if err := w.Close(); err != nil {
		return nil, err
	}
	return out.Bytes(), nil
}

func (e *engine) metricsTicker() {
	t := time.NewTicker(1 * time.Second)
	defer t.Stop()
	for {
		select {
		case <-t.C:
			for _, s := range e.shards {
				cur := atomic.LoadUint64(&s.bytesWritten)
				prev := atomic.LoadUint64(&s.lastTickBytes)
				if cur >= prev {
					atomic.StoreUint64(&s.ioBytesPerSec, cur-prev)
				}
				atomic.StoreUint64(&s.lastTickBytes, cur)
			}
		case <-e.quit:
			return
		}
	}
}

func readHeader(f *os.File) (fileHeader, error) {
	if _, err := f.Seek(0, io.SeekStart); err != nil {
		return fileHeader{}, err
	}
	var h fileHeader
	if err := binary.Read(f, binary.LittleEndian, &h.Magic); err != nil {
		return fileHeader{}, err
	}
	if err := binary.Read(f, binary.LittleEndian, &h.Version); err != nil {
		return fileHeader{}, err
	}
	if err := binary.Read(f, binary.LittleEndian, &h.EntryCount); err != nil {
		return fileHeader{}, err
	}
	if err := binary.Read(f, binary.LittleEndian, &h.LastOffset); err != nil {
		return fileHeader{}, err
	}
	return h, nil
}

func writeHeader(f *os.File, h fileHeader) error {
	if _, err := f.Seek(0, io.SeekStart); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, h.Magic); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, h.Version); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, h.EntryCount); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, h.LastOffset); err != nil {
		return err
	}
	return f.Sync()
}
