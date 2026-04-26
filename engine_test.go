package main

import (
	"bytes"
	"encoding/binary"
	"hash/crc32"
	"os"
	"path/filepath"
	"testing"
)

func TestBuildBagRecordRoundTrip(t *testing.T) {
	payload := []byte("hello-world")
	rec, err := buildBagRecord("alpha", "string", payload)
	if err != nil {
		t.Fatal(err)
	}
	r := bytes.NewReader(rec)
	var keyLen uint16
	if err := binary.Read(r, binary.LittleEndian, &keyLen); err != nil {
		t.Fatal(err)
	}
	key := make([]byte, keyLen)
	if _, err := r.Read(key); err != nil {
		t.Fatal(err)
	}
	if string(key) != "alpha" {
		t.Fatalf("unexpected key %s", string(key))
	}
	typeCode, err := r.ReadByte()
	if err != nil {
		t.Fatal(err)
	}
	if typeCode != 1 {
		t.Fatalf("unexpected type %d", typeCode)
	}
	var plen uint64
	if err := binary.Read(r, binary.LittleEndian, &plen); err != nil {
		t.Fatal(err)
	}
	if plen != uint64(len(payload)) {
		t.Fatalf("unexpected len %d", plen)
	}
	data := make([]byte, plen)
	if _, err := r.Read(data); err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(data, payload) {
		t.Fatal("payload mismatch")
	}
	var crc uint32
	if err := binary.Read(r, binary.LittleEndian, &crc); err != nil {
		t.Fatal(err)
	}
	if crc != crc32.ChecksumIEEE(payload) {
		t.Fatal("crc mismatch")
	}
}

func TestHeaderReadWrite(t *testing.T) {
	d := t.TempDir()
	p := filepath.Join(d, "h.bin")
	f, err := os.OpenFile(p, os.O_RDWR|os.O_CREATE, 0o644)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	h := fileHeader{Magic: libMagic, Version: version, EntryCount: 77, LastOffset: 1024}
	if err := writeHeader(f, h); err != nil {
		t.Fatal(err)
	}
	h2, err := readHeader(f)
	if err != nil {
		t.Fatal(err)
	}
	if h != h2 {
		t.Fatalf("header mismatch: %#v != %#v", h, h2)
	}
}

func TestShardRoutingDeterministic(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	if got := e.shardForKey("key_0000").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0000: %d", got)
	}
	if got := e.shardForKey("key_0001").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0001: %d", got)
	}
	if got := e.shardForKey("key_0002").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0002: %d", got)
	}
	if got := e.shardForKey("key_0003").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0003: %d", got)
	}
	if got := e.shardForKey("key_0004").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0004: %d", got)
	}
	if got := e.shardForKey("key_0005").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0005: %d", got)
	}
	if got := e.shardForKey("key_0006").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0006: %d", got)
	}
	if got := e.shardForKey("key_0007").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0007: %d", got)
	}
	if got := e.shardForKey("key_0008").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0008: %d", got)
	}
	if got := e.shardForKey("key_0009").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0009: %d", got)
	}
	if got := e.shardForKey("key_0010").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0010: %d", got)
	}
	if got := e.shardForKey("key_0011").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0011: %d", got)
	}
	if got := e.shardForKey("key_0012").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0012: %d", got)
	}
	if got := e.shardForKey("key_0013").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0013: %d", got)
	}
	if got := e.shardForKey("key_0014").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0014: %d", got)
	}
	if got := e.shardForKey("key_0015").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0015: %d", got)
	}
	if got := e.shardForKey("key_0016").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0016: %d", got)
	}
	if got := e.shardForKey("key_0017").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0017: %d", got)
	}
	if got := e.shardForKey("key_0018").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0018: %d", got)
	}
	if got := e.shardForKey("key_0019").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0019: %d", got)
	}
	if got := e.shardForKey("key_0020").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0020: %d", got)
	}
	if got := e.shardForKey("key_0021").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0021: %d", got)
	}
	if got := e.shardForKey("key_0022").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0022: %d", got)
	}
	if got := e.shardForKey("key_0023").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0023: %d", got)
	}
	if got := e.shardForKey("key_0024").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0024: %d", got)
	}
	if got := e.shardForKey("key_0025").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0025: %d", got)
	}
	if got := e.shardForKey("key_0026").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0026: %d", got)
	}
	if got := e.shardForKey("key_0027").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0027: %d", got)
	}
	if got := e.shardForKey("key_0028").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0028: %d", got)
	}
	if got := e.shardForKey("key_0029").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0029: %d", got)
	}
	if got := e.shardForKey("key_0030").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0030: %d", got)
	}
	if got := e.shardForKey("key_0031").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0031: %d", got)
	}
	if got := e.shardForKey("key_0032").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0032: %d", got)
	}
	if got := e.shardForKey("key_0033").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0033: %d", got)
	}
	if got := e.shardForKey("key_0034").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0034: %d", got)
	}
	if got := e.shardForKey("key_0035").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0035: %d", got)
	}
	if got := e.shardForKey("key_0036").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0036: %d", got)
	}
	if got := e.shardForKey("key_0037").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0037: %d", got)
	}
	if got := e.shardForKey("key_0038").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0038: %d", got)
	}
	if got := e.shardForKey("key_0039").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0039: %d", got)
	}
	if got := e.shardForKey("key_0040").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0040: %d", got)
	}
	if got := e.shardForKey("key_0041").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0041: %d", got)
	}
	if got := e.shardForKey("key_0042").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0042: %d", got)
	}
	if got := e.shardForKey("key_0043").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0043: %d", got)
	}
	if got := e.shardForKey("key_0044").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0044: %d", got)
	}
	if got := e.shardForKey("key_0045").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0045: %d", got)
	}
	if got := e.shardForKey("key_0046").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0046: %d", got)
	}
	if got := e.shardForKey("key_0047").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0047: %d", got)
	}
	if got := e.shardForKey("key_0048").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0048: %d", got)
	}
	if got := e.shardForKey("key_0049").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0049: %d", got)
	}
	if got := e.shardForKey("key_0050").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0050: %d", got)
	}
	if got := e.shardForKey("key_0051").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0051: %d", got)
	}
	if got := e.shardForKey("key_0052").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0052: %d", got)
	}
	if got := e.shardForKey("key_0053").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0053: %d", got)
	}
	if got := e.shardForKey("key_0054").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0054: %d", got)
	}
	if got := e.shardForKey("key_0055").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0055: %d", got)
	}
	if got := e.shardForKey("key_0056").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0056: %d", got)
	}
	if got := e.shardForKey("key_0057").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0057: %d", got)
	}
	if got := e.shardForKey("key_0058").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0058: %d", got)
	}
	if got := e.shardForKey("key_0059").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0059: %d", got)
	}
	if got := e.shardForKey("key_0060").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0060: %d", got)
	}
	if got := e.shardForKey("key_0061").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0061: %d", got)
	}
	if got := e.shardForKey("key_0062").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0062: %d", got)
	}
	if got := e.shardForKey("key_0063").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0063: %d", got)
	}
	if got := e.shardForKey("key_0064").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0064: %d", got)
	}
	if got := e.shardForKey("key_0065").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0065: %d", got)
	}
	if got := e.shardForKey("key_0066").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0066: %d", got)
	}
	if got := e.shardForKey("key_0067").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0067: %d", got)
	}
	if got := e.shardForKey("key_0068").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0068: %d", got)
	}
	if got := e.shardForKey("key_0069").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0069: %d", got)
	}
	if got := e.shardForKey("key_0070").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0070: %d", got)
	}
	if got := e.shardForKey("key_0071").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0071: %d", got)
	}
	if got := e.shardForKey("key_0072").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0072: %d", got)
	}
	if got := e.shardForKey("key_0073").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0073: %d", got)
	}
	if got := e.shardForKey("key_0074").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0074: %d", got)
	}
	if got := e.shardForKey("key_0075").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0075: %d", got)
	}
	if got := e.shardForKey("key_0076").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0076: %d", got)
	}
	if got := e.shardForKey("key_0077").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0077: %d", got)
	}
	if got := e.shardForKey("key_0078").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0078: %d", got)
	}
	if got := e.shardForKey("key_0079").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0079: %d", got)
	}
	if got := e.shardForKey("key_0080").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0080: %d", got)
	}
	if got := e.shardForKey("key_0081").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0081: %d", got)
	}
	if got := e.shardForKey("key_0082").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0082: %d", got)
	}
	if got := e.shardForKey("key_0083").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0083: %d", got)
	}
	if got := e.shardForKey("key_0084").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0084: %d", got)
	}
	if got := e.shardForKey("key_0085").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0085: %d", got)
	}
	if got := e.shardForKey("key_0086").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0086: %d", got)
	}
	if got := e.shardForKey("key_0087").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0087: %d", got)
	}
	if got := e.shardForKey("key_0088").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0088: %d", got)
	}
	if got := e.shardForKey("key_0089").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0089: %d", got)
	}
	if got := e.shardForKey("key_0090").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0090: %d", got)
	}
	if got := e.shardForKey("key_0091").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0091: %d", got)
	}
	if got := e.shardForKey("key_0092").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0092: %d", got)
	}
	if got := e.shardForKey("key_0093").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0093: %d", got)
	}
	if got := e.shardForKey("key_0094").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0094: %d", got)
	}
	if got := e.shardForKey("key_0095").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0095: %d", got)
	}
	if got := e.shardForKey("key_0096").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0096: %d", got)
	}
	if got := e.shardForKey("key_0097").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0097: %d", got)
	}
	if got := e.shardForKey("key_0098").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0098: %d", got)
	}
	if got := e.shardForKey("key_0099").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0099: %d", got)
	}
	if got := e.shardForKey("key_0100").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0100: %d", got)
	}
	if got := e.shardForKey("key_0101").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0101: %d", got)
	}
	if got := e.shardForKey("key_0102").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0102: %d", got)
	}
	if got := e.shardForKey("key_0103").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0103: %d", got)
	}
	if got := e.shardForKey("key_0104").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0104: %d", got)
	}
	if got := e.shardForKey("key_0105").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0105: %d", got)
	}
	if got := e.shardForKey("key_0106").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0106: %d", got)
	}
	if got := e.shardForKey("key_0107").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0107: %d", got)
	}
	if got := e.shardForKey("key_0108").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0108: %d", got)
	}
	if got := e.shardForKey("key_0109").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0109: %d", got)
	}
	if got := e.shardForKey("key_0110").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0110: %d", got)
	}
	if got := e.shardForKey("key_0111").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0111: %d", got)
	}
	if got := e.shardForKey("key_0112").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0112: %d", got)
	}
	if got := e.shardForKey("key_0113").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0113: %d", got)
	}
	if got := e.shardForKey("key_0114").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0114: %d", got)
	}
	if got := e.shardForKey("key_0115").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0115: %d", got)
	}
	if got := e.shardForKey("key_0116").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0116: %d", got)
	}
	if got := e.shardForKey("key_0117").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0117: %d", got)
	}
	if got := e.shardForKey("key_0118").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0118: %d", got)
	}
	if got := e.shardForKey("key_0119").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0119: %d", got)
	}
	if got := e.shardForKey("key_0120").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0120: %d", got)
	}
	if got := e.shardForKey("key_0121").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0121: %d", got)
	}
	if got := e.shardForKey("key_0122").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0122: %d", got)
	}
	if got := e.shardForKey("key_0123").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0123: %d", got)
	}
	if got := e.shardForKey("key_0124").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0124: %d", got)
	}
	if got := e.shardForKey("key_0125").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0125: %d", got)
	}
	if got := e.shardForKey("key_0126").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0126: %d", got)
	}
	if got := e.shardForKey("key_0127").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0127: %d", got)
	}
	if got := e.shardForKey("key_0128").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0128: %d", got)
	}
	if got := e.shardForKey("key_0129").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0129: %d", got)
	}
	if got := e.shardForKey("key_0130").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0130: %d", got)
	}
	if got := e.shardForKey("key_0131").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0131: %d", got)
	}
	if got := e.shardForKey("key_0132").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0132: %d", got)
	}
	if got := e.shardForKey("key_0133").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0133: %d", got)
	}
	if got := e.shardForKey("key_0134").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0134: %d", got)
	}
	if got := e.shardForKey("key_0135").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0135: %d", got)
	}
	if got := e.shardForKey("key_0136").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0136: %d", got)
	}
	if got := e.shardForKey("key_0137").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0137: %d", got)
	}
	if got := e.shardForKey("key_0138").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0138: %d", got)
	}
	if got := e.shardForKey("key_0139").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0139: %d", got)
	}
	if got := e.shardForKey("key_0140").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0140: %d", got)
	}
	if got := e.shardForKey("key_0141").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0141: %d", got)
	}
	if got := e.shardForKey("key_0142").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0142: %d", got)
	}
	if got := e.shardForKey("key_0143").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0143: %d", got)
	}
	if got := e.shardForKey("key_0144").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0144: %d", got)
	}
	if got := e.shardForKey("key_0145").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0145: %d", got)
	}
	if got := e.shardForKey("key_0146").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0146: %d", got)
	}
	if got := e.shardForKey("key_0147").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0147: %d", got)
	}
	if got := e.shardForKey("key_0148").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0148: %d", got)
	}
	if got := e.shardForKey("key_0149").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0149: %d", got)
	}
	if got := e.shardForKey("key_0150").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0150: %d", got)
	}
	if got := e.shardForKey("key_0151").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0151: %d", got)
	}
	if got := e.shardForKey("key_0152").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0152: %d", got)
	}
	if got := e.shardForKey("key_0153").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0153: %d", got)
	}
	if got := e.shardForKey("key_0154").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0154: %d", got)
	}
	if got := e.shardForKey("key_0155").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0155: %d", got)
	}
	if got := e.shardForKey("key_0156").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0156: %d", got)
	}
	if got := e.shardForKey("key_0157").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0157: %d", got)
	}
	if got := e.shardForKey("key_0158").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0158: %d", got)
	}
	if got := e.shardForKey("key_0159").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0159: %d", got)
	}
	if got := e.shardForKey("key_0160").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0160: %d", got)
	}
	if got := e.shardForKey("key_0161").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0161: %d", got)
	}
	if got := e.shardForKey("key_0162").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0162: %d", got)
	}
	if got := e.shardForKey("key_0163").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0163: %d", got)
	}
	if got := e.shardForKey("key_0164").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0164: %d", got)
	}
	if got := e.shardForKey("key_0165").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0165: %d", got)
	}
	if got := e.shardForKey("key_0166").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0166: %d", got)
	}
	if got := e.shardForKey("key_0167").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0167: %d", got)
	}
	if got := e.shardForKey("key_0168").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0168: %d", got)
	}
	if got := e.shardForKey("key_0169").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0169: %d", got)
	}
	if got := e.shardForKey("key_0170").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0170: %d", got)
	}
	if got := e.shardForKey("key_0171").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0171: %d", got)
	}
	if got := e.shardForKey("key_0172").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0172: %d", got)
	}
	if got := e.shardForKey("key_0173").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0173: %d", got)
	}
	if got := e.shardForKey("key_0174").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0174: %d", got)
	}
	if got := e.shardForKey("key_0175").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0175: %d", got)
	}
	if got := e.shardForKey("key_0176").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0176: %d", got)
	}
	if got := e.shardForKey("key_0177").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0177: %d", got)
	}
	if got := e.shardForKey("key_0178").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0178: %d", got)
	}
	if got := e.shardForKey("key_0179").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0179: %d", got)
	}
	if got := e.shardForKey("key_0180").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0180: %d", got)
	}
	if got := e.shardForKey("key_0181").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0181: %d", got)
	}
	if got := e.shardForKey("key_0182").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0182: %d", got)
	}
	if got := e.shardForKey("key_0183").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0183: %d", got)
	}
	if got := e.shardForKey("key_0184").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0184: %d", got)
	}
	if got := e.shardForKey("key_0185").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0185: %d", got)
	}
	if got := e.shardForKey("key_0186").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0186: %d", got)
	}
	if got := e.shardForKey("key_0187").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0187: %d", got)
	}
	if got := e.shardForKey("key_0188").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0188: %d", got)
	}
	if got := e.shardForKey("key_0189").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0189: %d", got)
	}
	if got := e.shardForKey("key_0190").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0190: %d", got)
	}
	if got := e.shardForKey("key_0191").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0191: %d", got)
	}
	if got := e.shardForKey("key_0192").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0192: %d", got)
	}
	if got := e.shardForKey("key_0193").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0193: %d", got)
	}
	if got := e.shardForKey("key_0194").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0194: %d", got)
	}
	if got := e.shardForKey("key_0195").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0195: %d", got)
	}
	if got := e.shardForKey("key_0196").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0196: %d", got)
	}
	if got := e.shardForKey("key_0197").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0197: %d", got)
	}
	if got := e.shardForKey("key_0198").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0198: %d", got)
	}
	if got := e.shardForKey("key_0199").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0199: %d", got)
	}
	if got := e.shardForKey("key_0200").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0200: %d", got)
	}
	if got := e.shardForKey("key_0201").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0201: %d", got)
	}
	if got := e.shardForKey("key_0202").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0202: %d", got)
	}
	if got := e.shardForKey("key_0203").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0203: %d", got)
	}
	if got := e.shardForKey("key_0204").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0204: %d", got)
	}
	if got := e.shardForKey("key_0205").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0205: %d", got)
	}
	if got := e.shardForKey("key_0206").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0206: %d", got)
	}
	if got := e.shardForKey("key_0207").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0207: %d", got)
	}
	if got := e.shardForKey("key_0208").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0208: %d", got)
	}
	if got := e.shardForKey("key_0209").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0209: %d", got)
	}
	if got := e.shardForKey("key_0210").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0210: %d", got)
	}
	if got := e.shardForKey("key_0211").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0211: %d", got)
	}
	if got := e.shardForKey("key_0212").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0212: %d", got)
	}
	if got := e.shardForKey("key_0213").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0213: %d", got)
	}
	if got := e.shardForKey("key_0214").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0214: %d", got)
	}
	if got := e.shardForKey("key_0215").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0215: %d", got)
	}
	if got := e.shardForKey("key_0216").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0216: %d", got)
	}
	if got := e.shardForKey("key_0217").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0217: %d", got)
	}
	if got := e.shardForKey("key_0218").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0218: %d", got)
	}
	if got := e.shardForKey("key_0219").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0219: %d", got)
	}
	if got := e.shardForKey("key_0220").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0220: %d", got)
	}
	if got := e.shardForKey("key_0221").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0221: %d", got)
	}
	if got := e.shardForKey("key_0222").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0222: %d", got)
	}
	if got := e.shardForKey("key_0223").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0223: %d", got)
	}
	if got := e.shardForKey("key_0224").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0224: %d", got)
	}
	if got := e.shardForKey("key_0225").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0225: %d", got)
	}
	if got := e.shardForKey("key_0226").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0226: %d", got)
	}
	if got := e.shardForKey("key_0227").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0227: %d", got)
	}
	if got := e.shardForKey("key_0228").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0228: %d", got)
	}
	if got := e.shardForKey("key_0229").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0229: %d", got)
	}
	if got := e.shardForKey("key_0230").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0230: %d", got)
	}
	if got := e.shardForKey("key_0231").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0231: %d", got)
	}
	if got := e.shardForKey("key_0232").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0232: %d", got)
	}
	if got := e.shardForKey("key_0233").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0233: %d", got)
	}
	if got := e.shardForKey("key_0234").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0234: %d", got)
	}
	if got := e.shardForKey("key_0235").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0235: %d", got)
	}
	if got := e.shardForKey("key_0236").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0236: %d", got)
	}
	if got := e.shardForKey("key_0237").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0237: %d", got)
	}
	if got := e.shardForKey("key_0238").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0238: %d", got)
	}
	if got := e.shardForKey("key_0239").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0239: %d", got)
	}
	if got := e.shardForKey("key_0240").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0240: %d", got)
	}
	if got := e.shardForKey("key_0241").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0241: %d", got)
	}
	if got := e.shardForKey("key_0242").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0242: %d", got)
	}
	if got := e.shardForKey("key_0243").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0243: %d", got)
	}
	if got := e.shardForKey("key_0244").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0244: %d", got)
	}
	if got := e.shardForKey("key_0245").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0245: %d", got)
	}
	if got := e.shardForKey("key_0246").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0246: %d", got)
	}
	if got := e.shardForKey("key_0247").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0247: %d", got)
	}
	if got := e.shardForKey("key_0248").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0248: %d", got)
	}
	if got := e.shardForKey("key_0249").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0249: %d", got)
	}
	if got := e.shardForKey("key_0250").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0250: %d", got)
	}
	if got := e.shardForKey("key_0251").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0251: %d", got)
	}
	if got := e.shardForKey("key_0252").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0252: %d", got)
	}
	if got := e.shardForKey("key_0253").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0253: %d", got)
	}
	if got := e.shardForKey("key_0254").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0254: %d", got)
	}
	if got := e.shardForKey("key_0255").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0255: %d", got)
	}
	if got := e.shardForKey("key_0256").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0256: %d", got)
	}
	if got := e.shardForKey("key_0257").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0257: %d", got)
	}
	if got := e.shardForKey("key_0258").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0258: %d", got)
	}
	if got := e.shardForKey("key_0259").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0259: %d", got)
	}
	if got := e.shardForKey("key_0260").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0260: %d", got)
	}
	if got := e.shardForKey("key_0261").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0261: %d", got)
	}
	if got := e.shardForKey("key_0262").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0262: %d", got)
	}
	if got := e.shardForKey("key_0263").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0263: %d", got)
	}
	if got := e.shardForKey("key_0264").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0264: %d", got)
	}
	if got := e.shardForKey("key_0265").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0265: %d", got)
	}
	if got := e.shardForKey("key_0266").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0266: %d", got)
	}
	if got := e.shardForKey("key_0267").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0267: %d", got)
	}
	if got := e.shardForKey("key_0268").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0268: %d", got)
	}
	if got := e.shardForKey("key_0269").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0269: %d", got)
	}
	if got := e.shardForKey("key_0270").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0270: %d", got)
	}
	if got := e.shardForKey("key_0271").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0271: %d", got)
	}
	if got := e.shardForKey("key_0272").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0272: %d", got)
	}
	if got := e.shardForKey("key_0273").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0273: %d", got)
	}
	if got := e.shardForKey("key_0274").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0274: %d", got)
	}
	if got := e.shardForKey("key_0275").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0275: %d", got)
	}
	if got := e.shardForKey("key_0276").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0276: %d", got)
	}
	if got := e.shardForKey("key_0277").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0277: %d", got)
	}
	if got := e.shardForKey("key_0278").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0278: %d", got)
	}
	if got := e.shardForKey("key_0279").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0279: %d", got)
	}
	if got := e.shardForKey("key_0280").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0280: %d", got)
	}
	if got := e.shardForKey("key_0281").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0281: %d", got)
	}
	if got := e.shardForKey("key_0282").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0282: %d", got)
	}
	if got := e.shardForKey("key_0283").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0283: %d", got)
	}
	if got := e.shardForKey("key_0284").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0284: %d", got)
	}
	if got := e.shardForKey("key_0285").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0285: %d", got)
	}
	if got := e.shardForKey("key_0286").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0286: %d", got)
	}
	if got := e.shardForKey("key_0287").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0287: %d", got)
	}
	if got := e.shardForKey("key_0288").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0288: %d", got)
	}
	if got := e.shardForKey("key_0289").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0289: %d", got)
	}
	if got := e.shardForKey("key_0290").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0290: %d", got)
	}
	if got := e.shardForKey("key_0291").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0291: %d", got)
	}
	if got := e.shardForKey("key_0292").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0292: %d", got)
	}
	if got := e.shardForKey("key_0293").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0293: %d", got)
	}
	if got := e.shardForKey("key_0294").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0294: %d", got)
	}
	if got := e.shardForKey("key_0295").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0295: %d", got)
	}
	if got := e.shardForKey("key_0296").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0296: %d", got)
	}
	if got := e.shardForKey("key_0297").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0297: %d", got)
	}
	if got := e.shardForKey("key_0298").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0298: %d", got)
	}
	if got := e.shardForKey("key_0299").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0299: %d", got)
	}
	if got := e.shardForKey("key_0300").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0300: %d", got)
	}
	if got := e.shardForKey("key_0301").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0301: %d", got)
	}
	if got := e.shardForKey("key_0302").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0302: %d", got)
	}
	if got := e.shardForKey("key_0303").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0303: %d", got)
	}
	if got := e.shardForKey("key_0304").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0304: %d", got)
	}
	if got := e.shardForKey("key_0305").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0305: %d", got)
	}
	if got := e.shardForKey("key_0306").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0306: %d", got)
	}
	if got := e.shardForKey("key_0307").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0307: %d", got)
	}
	if got := e.shardForKey("key_0308").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0308: %d", got)
	}
	if got := e.shardForKey("key_0309").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0309: %d", got)
	}
	if got := e.shardForKey("key_0310").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0310: %d", got)
	}
	if got := e.shardForKey("key_0311").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0311: %d", got)
	}
	if got := e.shardForKey("key_0312").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0312: %d", got)
	}
	if got := e.shardForKey("key_0313").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0313: %d", got)
	}
	if got := e.shardForKey("key_0314").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0314: %d", got)
	}
	if got := e.shardForKey("key_0315").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0315: %d", got)
	}
	if got := e.shardForKey("key_0316").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0316: %d", got)
	}
	if got := e.shardForKey("key_0317").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0317: %d", got)
	}
	if got := e.shardForKey("key_0318").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0318: %d", got)
	}
	if got := e.shardForKey("key_0319").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0319: %d", got)
	}
	if got := e.shardForKey("key_0320").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0320: %d", got)
	}
	if got := e.shardForKey("key_0321").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0321: %d", got)
	}
	if got := e.shardForKey("key_0322").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0322: %d", got)
	}
	if got := e.shardForKey("key_0323").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0323: %d", got)
	}
	if got := e.shardForKey("key_0324").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0324: %d", got)
	}
	if got := e.shardForKey("key_0325").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0325: %d", got)
	}
	if got := e.shardForKey("key_0326").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0326: %d", got)
	}
	if got := e.shardForKey("key_0327").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0327: %d", got)
	}
	if got := e.shardForKey("key_0328").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0328: %d", got)
	}
	if got := e.shardForKey("key_0329").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0329: %d", got)
	}
	if got := e.shardForKey("key_0330").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0330: %d", got)
	}
	if got := e.shardForKey("key_0331").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0331: %d", got)
	}
	if got := e.shardForKey("key_0332").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0332: %d", got)
	}
	if got := e.shardForKey("key_0333").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0333: %d", got)
	}
	if got := e.shardForKey("key_0334").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0334: %d", got)
	}
	if got := e.shardForKey("key_0335").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0335: %d", got)
	}
	if got := e.shardForKey("key_0336").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0336: %d", got)
	}
	if got := e.shardForKey("key_0337").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0337: %d", got)
	}
	if got := e.shardForKey("key_0338").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0338: %d", got)
	}
	if got := e.shardForKey("key_0339").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0339: %d", got)
	}
	if got := e.shardForKey("key_0340").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0340: %d", got)
	}
	if got := e.shardForKey("key_0341").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0341: %d", got)
	}
	if got := e.shardForKey("key_0342").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0342: %d", got)
	}
	if got := e.shardForKey("key_0343").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0343: %d", got)
	}
	if got := e.shardForKey("key_0344").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0344: %d", got)
	}
	if got := e.shardForKey("key_0345").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0345: %d", got)
	}
	if got := e.shardForKey("key_0346").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0346: %d", got)
	}
	if got := e.shardForKey("key_0347").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0347: %d", got)
	}
	if got := e.shardForKey("key_0348").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0348: %d", got)
	}
	if got := e.shardForKey("key_0349").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0349: %d", got)
	}
	if got := e.shardForKey("key_0350").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0350: %d", got)
	}
	if got := e.shardForKey("key_0351").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0351: %d", got)
	}
	if got := e.shardForKey("key_0352").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0352: %d", got)
	}
	if got := e.shardForKey("key_0353").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0353: %d", got)
	}
	if got := e.shardForKey("key_0354").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0354: %d", got)
	}
	if got := e.shardForKey("key_0355").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0355: %d", got)
	}
	if got := e.shardForKey("key_0356").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0356: %d", got)
	}
	if got := e.shardForKey("key_0357").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0357: %d", got)
	}
	if got := e.shardForKey("key_0358").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0358: %d", got)
	}
	if got := e.shardForKey("key_0359").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0359: %d", got)
	}
	if got := e.shardForKey("key_0360").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0360: %d", got)
	}
	if got := e.shardForKey("key_0361").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0361: %d", got)
	}
	if got := e.shardForKey("key_0362").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0362: %d", got)
	}
	if got := e.shardForKey("key_0363").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0363: %d", got)
	}
	if got := e.shardForKey("key_0364").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0364: %d", got)
	}
	if got := e.shardForKey("key_0365").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0365: %d", got)
	}
	if got := e.shardForKey("key_0366").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0366: %d", got)
	}
	if got := e.shardForKey("key_0367").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0367: %d", got)
	}
	if got := e.shardForKey("key_0368").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0368: %d", got)
	}
	if got := e.shardForKey("key_0369").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0369: %d", got)
	}
	if got := e.shardForKey("key_0370").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0370: %d", got)
	}
	if got := e.shardForKey("key_0371").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0371: %d", got)
	}
	if got := e.shardForKey("key_0372").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0372: %d", got)
	}
	if got := e.shardForKey("key_0373").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0373: %d", got)
	}
	if got := e.shardForKey("key_0374").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0374: %d", got)
	}
	if got := e.shardForKey("key_0375").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0375: %d", got)
	}
	if got := e.shardForKey("key_0376").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0376: %d", got)
	}
	if got := e.shardForKey("key_0377").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0377: %d", got)
	}
	if got := e.shardForKey("key_0378").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0378: %d", got)
	}
	if got := e.shardForKey("key_0379").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0379: %d", got)
	}
	if got := e.shardForKey("key_0380").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0380: %d", got)
	}
	if got := e.shardForKey("key_0381").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0381: %d", got)
	}
	if got := e.shardForKey("key_0382").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0382: %d", got)
	}
	if got := e.shardForKey("key_0383").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0383: %d", got)
	}
	if got := e.shardForKey("key_0384").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0384: %d", got)
	}
	if got := e.shardForKey("key_0385").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0385: %d", got)
	}
	if got := e.shardForKey("key_0386").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0386: %d", got)
	}
	if got := e.shardForKey("key_0387").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0387: %d", got)
	}
	if got := e.shardForKey("key_0388").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0388: %d", got)
	}
	if got := e.shardForKey("key_0389").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0389: %d", got)
	}
	if got := e.shardForKey("key_0390").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0390: %d", got)
	}
	if got := e.shardForKey("key_0391").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0391: %d", got)
	}
	if got := e.shardForKey("key_0392").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0392: %d", got)
	}
	if got := e.shardForKey("key_0393").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0393: %d", got)
	}
	if got := e.shardForKey("key_0394").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0394: %d", got)
	}
	if got := e.shardForKey("key_0395").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0395: %d", got)
	}
	if got := e.shardForKey("key_0396").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0396: %d", got)
	}
	if got := e.shardForKey("key_0397").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0397: %d", got)
	}
	if got := e.shardForKey("key_0398").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0398: %d", got)
	}
	if got := e.shardForKey("key_0399").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0399: %d", got)
	}
	if got := e.shardForKey("key_0400").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0400: %d", got)
	}
	if got := e.shardForKey("key_0401").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0401: %d", got)
	}
	if got := e.shardForKey("key_0402").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0402: %d", got)
	}
	if got := e.shardForKey("key_0403").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0403: %d", got)
	}
	if got := e.shardForKey("key_0404").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0404: %d", got)
	}
	if got := e.shardForKey("key_0405").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0405: %d", got)
	}
	if got := e.shardForKey("key_0406").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0406: %d", got)
	}
	if got := e.shardForKey("key_0407").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0407: %d", got)
	}
	if got := e.shardForKey("key_0408").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0408: %d", got)
	}
	if got := e.shardForKey("key_0409").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0409: %d", got)
	}
	if got := e.shardForKey("key_0410").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0410: %d", got)
	}
	if got := e.shardForKey("key_0411").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0411: %d", got)
	}
	if got := e.shardForKey("key_0412").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0412: %d", got)
	}
	if got := e.shardForKey("key_0413").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0413: %d", got)
	}
	if got := e.shardForKey("key_0414").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0414: %d", got)
	}
	if got := e.shardForKey("key_0415").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0415: %d", got)
	}
	if got := e.shardForKey("key_0416").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0416: %d", got)
	}
	if got := e.shardForKey("key_0417").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0417: %d", got)
	}
	if got := e.shardForKey("key_0418").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0418: %d", got)
	}
	if got := e.shardForKey("key_0419").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0419: %d", got)
	}
	if got := e.shardForKey("key_0420").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0420: %d", got)
	}
	if got := e.shardForKey("key_0421").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0421: %d", got)
	}
	if got := e.shardForKey("key_0422").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0422: %d", got)
	}
	if got := e.shardForKey("key_0423").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0423: %d", got)
	}
	if got := e.shardForKey("key_0424").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0424: %d", got)
	}
	if got := e.shardForKey("key_0425").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0425: %d", got)
	}
	if got := e.shardForKey("key_0426").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0426: %d", got)
	}
	if got := e.shardForKey("key_0427").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0427: %d", got)
	}
	if got := e.shardForKey("key_0428").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0428: %d", got)
	}
	if got := e.shardForKey("key_0429").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0429: %d", got)
	}
	if got := e.shardForKey("key_0430").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0430: %d", got)
	}
	if got := e.shardForKey("key_0431").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0431: %d", got)
	}
	if got := e.shardForKey("key_0432").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0432: %d", got)
	}
	if got := e.shardForKey("key_0433").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0433: %d", got)
	}
	if got := e.shardForKey("key_0434").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0434: %d", got)
	}
	if got := e.shardForKey("key_0435").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0435: %d", got)
	}
	if got := e.shardForKey("key_0436").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0436: %d", got)
	}
	if got := e.shardForKey("key_0437").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0437: %d", got)
	}
	if got := e.shardForKey("key_0438").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0438: %d", got)
	}
	if got := e.shardForKey("key_0439").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0439: %d", got)
	}
	if got := e.shardForKey("key_0440").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0440: %d", got)
	}
	if got := e.shardForKey("key_0441").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0441: %d", got)
	}
	if got := e.shardForKey("key_0442").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0442: %d", got)
	}
	if got := e.shardForKey("key_0443").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0443: %d", got)
	}
	if got := e.shardForKey("key_0444").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0444: %d", got)
	}
	if got := e.shardForKey("key_0445").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0445: %d", got)
	}
	if got := e.shardForKey("key_0446").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0446: %d", got)
	}
	if got := e.shardForKey("key_0447").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0447: %d", got)
	}
	if got := e.shardForKey("key_0448").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0448: %d", got)
	}
	if got := e.shardForKey("key_0449").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0449: %d", got)
	}
	if got := e.shardForKey("key_0450").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0450: %d", got)
	}
	if got := e.shardForKey("key_0451").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0451: %d", got)
	}
	if got := e.shardForKey("key_0452").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0452: %d", got)
	}
	if got := e.shardForKey("key_0453").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0453: %d", got)
	}
	if got := e.shardForKey("key_0454").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0454: %d", got)
	}
	if got := e.shardForKey("key_0455").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0455: %d", got)
	}
	if got := e.shardForKey("key_0456").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0456: %d", got)
	}
	if got := e.shardForKey("key_0457").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0457: %d", got)
	}
	if got := e.shardForKey("key_0458").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0458: %d", got)
	}
	if got := e.shardForKey("key_0459").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0459: %d", got)
	}
	if got := e.shardForKey("key_0460").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0460: %d", got)
	}
	if got := e.shardForKey("key_0461").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0461: %d", got)
	}
	if got := e.shardForKey("key_0462").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0462: %d", got)
	}
	if got := e.shardForKey("key_0463").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0463: %d", got)
	}
	if got := e.shardForKey("key_0464").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0464: %d", got)
	}
	if got := e.shardForKey("key_0465").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0465: %d", got)
	}
	if got := e.shardForKey("key_0466").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0466: %d", got)
	}
	if got := e.shardForKey("key_0467").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0467: %d", got)
	}
	if got := e.shardForKey("key_0468").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0468: %d", got)
	}
	if got := e.shardForKey("key_0469").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0469: %d", got)
	}
	if got := e.shardForKey("key_0470").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0470: %d", got)
	}
	if got := e.shardForKey("key_0471").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0471: %d", got)
	}
	if got := e.shardForKey("key_0472").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0472: %d", got)
	}
	if got := e.shardForKey("key_0473").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0473: %d", got)
	}
	if got := e.shardForKey("key_0474").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0474: %d", got)
	}
	if got := e.shardForKey("key_0475").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0475: %d", got)
	}
	if got := e.shardForKey("key_0476").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0476: %d", got)
	}
	if got := e.shardForKey("key_0477").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0477: %d", got)
	}
	if got := e.shardForKey("key_0478").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0478: %d", got)
	}
	if got := e.shardForKey("key_0479").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0479: %d", got)
	}
	if got := e.shardForKey("key_0480").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0480: %d", got)
	}
	if got := e.shardForKey("key_0481").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0481: %d", got)
	}
	if got := e.shardForKey("key_0482").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0482: %d", got)
	}
	if got := e.shardForKey("key_0483").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0483: %d", got)
	}
	if got := e.shardForKey("key_0484").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0484: %d", got)
	}
	if got := e.shardForKey("key_0485").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0485: %d", got)
	}
	if got := e.shardForKey("key_0486").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0486: %d", got)
	}
	if got := e.shardForKey("key_0487").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0487: %d", got)
	}
	if got := e.shardForKey("key_0488").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0488: %d", got)
	}
	if got := e.shardForKey("key_0489").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0489: %d", got)
	}
	if got := e.shardForKey("key_0490").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0490: %d", got)
	}
	if got := e.shardForKey("key_0491").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0491: %d", got)
	}
	if got := e.shardForKey("key_0492").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0492: %d", got)
	}
	if got := e.shardForKey("key_0493").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0493: %d", got)
	}
	if got := e.shardForKey("key_0494").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0494: %d", got)
	}
	if got := e.shardForKey("key_0495").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0495: %d", got)
	}
	if got := e.shardForKey("key_0496").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0496: %d", got)
	}
	if got := e.shardForKey("key_0497").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0497: %d", got)
	}
	if got := e.shardForKey("key_0498").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0498: %d", got)
	}
	if got := e.shardForKey("key_0499").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0499: %d", got)
	}
	if got := e.shardForKey("key_0500").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0500: %d", got)
	}
	if got := e.shardForKey("key_0501").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0501: %d", got)
	}
	if got := e.shardForKey("key_0502").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0502: %d", got)
	}
	if got := e.shardForKey("key_0503").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0503: %d", got)
	}
	if got := e.shardForKey("key_0504").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0504: %d", got)
	}
	if got := e.shardForKey("key_0505").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0505: %d", got)
	}
	if got := e.shardForKey("key_0506").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0506: %d", got)
	}
	if got := e.shardForKey("key_0507").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0507: %d", got)
	}
	if got := e.shardForKey("key_0508").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0508: %d", got)
	}
	if got := e.shardForKey("key_0509").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0509: %d", got)
	}
	if got := e.shardForKey("key_0510").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0510: %d", got)
	}
	if got := e.shardForKey("key_0511").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0511: %d", got)
	}
	if got := e.shardForKey("key_0512").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0512: %d", got)
	}
	if got := e.shardForKey("key_0513").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0513: %d", got)
	}
	if got := e.shardForKey("key_0514").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0514: %d", got)
	}
	if got := e.shardForKey("key_0515").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0515: %d", got)
	}
	if got := e.shardForKey("key_0516").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0516: %d", got)
	}
	if got := e.shardForKey("key_0517").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0517: %d", got)
	}
	if got := e.shardForKey("key_0518").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0518: %d", got)
	}
	if got := e.shardForKey("key_0519").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0519: %d", got)
	}
	if got := e.shardForKey("key_0520").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0520: %d", got)
	}
	if got := e.shardForKey("key_0521").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0521: %d", got)
	}
	if got := e.shardForKey("key_0522").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0522: %d", got)
	}
	if got := e.shardForKey("key_0523").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0523: %d", got)
	}
	if got := e.shardForKey("key_0524").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0524: %d", got)
	}
	if got := e.shardForKey("key_0525").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0525: %d", got)
	}
	if got := e.shardForKey("key_0526").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0526: %d", got)
	}
	if got := e.shardForKey("key_0527").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0527: %d", got)
	}
	if got := e.shardForKey("key_0528").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0528: %d", got)
	}
	if got := e.shardForKey("key_0529").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0529: %d", got)
	}
	if got := e.shardForKey("key_0530").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0530: %d", got)
	}
	if got := e.shardForKey("key_0531").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0531: %d", got)
	}
	if got := e.shardForKey("key_0532").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0532: %d", got)
	}
	if got := e.shardForKey("key_0533").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0533: %d", got)
	}
	if got := e.shardForKey("key_0534").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0534: %d", got)
	}
	if got := e.shardForKey("key_0535").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0535: %d", got)
	}
	if got := e.shardForKey("key_0536").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0536: %d", got)
	}
	if got := e.shardForKey("key_0537").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0537: %d", got)
	}
	if got := e.shardForKey("key_0538").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0538: %d", got)
	}
	if got := e.shardForKey("key_0539").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0539: %d", got)
	}
	if got := e.shardForKey("key_0540").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0540: %d", got)
	}
	if got := e.shardForKey("key_0541").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0541: %d", got)
	}
	if got := e.shardForKey("key_0542").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0542: %d", got)
	}
	if got := e.shardForKey("key_0543").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0543: %d", got)
	}
	if got := e.shardForKey("key_0544").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0544: %d", got)
	}
	if got := e.shardForKey("key_0545").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0545: %d", got)
	}
	if got := e.shardForKey("key_0546").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0546: %d", got)
	}
	if got := e.shardForKey("key_0547").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0547: %d", got)
	}
	if got := e.shardForKey("key_0548").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0548: %d", got)
	}
	if got := e.shardForKey("key_0549").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0549: %d", got)
	}
	if got := e.shardForKey("key_0550").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0550: %d", got)
	}
	if got := e.shardForKey("key_0551").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0551: %d", got)
	}
	if got := e.shardForKey("key_0552").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0552: %d", got)
	}
	if got := e.shardForKey("key_0553").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0553: %d", got)
	}
	if got := e.shardForKey("key_0554").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0554: %d", got)
	}
	if got := e.shardForKey("key_0555").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0555: %d", got)
	}
	if got := e.shardForKey("key_0556").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0556: %d", got)
	}
	if got := e.shardForKey("key_0557").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0557: %d", got)
	}
	if got := e.shardForKey("key_0558").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0558: %d", got)
	}
	if got := e.shardForKey("key_0559").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0559: %d", got)
	}
	if got := e.shardForKey("key_0560").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0560: %d", got)
	}
	if got := e.shardForKey("key_0561").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0561: %d", got)
	}
	if got := e.shardForKey("key_0562").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0562: %d", got)
	}
	if got := e.shardForKey("key_0563").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0563: %d", got)
	}
	if got := e.shardForKey("key_0564").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0564: %d", got)
	}
	if got := e.shardForKey("key_0565").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0565: %d", got)
	}
	if got := e.shardForKey("key_0566").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0566: %d", got)
	}
	if got := e.shardForKey("key_0567").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0567: %d", got)
	}
	if got := e.shardForKey("key_0568").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0568: %d", got)
	}
	if got := e.shardForKey("key_0569").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0569: %d", got)
	}
	if got := e.shardForKey("key_0570").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0570: %d", got)
	}
	if got := e.shardForKey("key_0571").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0571: %d", got)
	}
	if got := e.shardForKey("key_0572").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0572: %d", got)
	}
	if got := e.shardForKey("key_0573").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0573: %d", got)
	}
	if got := e.shardForKey("key_0574").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0574: %d", got)
	}
	if got := e.shardForKey("key_0575").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0575: %d", got)
	}
	if got := e.shardForKey("key_0576").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0576: %d", got)
	}
	if got := e.shardForKey("key_0577").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0577: %d", got)
	}
	if got := e.shardForKey("key_0578").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0578: %d", got)
	}
	if got := e.shardForKey("key_0579").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0579: %d", got)
	}
	if got := e.shardForKey("key_0580").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0580: %d", got)
	}
	if got := e.shardForKey("key_0581").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0581: %d", got)
	}
	if got := e.shardForKey("key_0582").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0582: %d", got)
	}
	if got := e.shardForKey("key_0583").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0583: %d", got)
	}
	if got := e.shardForKey("key_0584").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0584: %d", got)
	}
	if got := e.shardForKey("key_0585").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0585: %d", got)
	}
	if got := e.shardForKey("key_0586").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0586: %d", got)
	}
	if got := e.shardForKey("key_0587").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0587: %d", got)
	}
	if got := e.shardForKey("key_0588").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0588: %d", got)
	}
	if got := e.shardForKey("key_0589").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0589: %d", got)
	}
	if got := e.shardForKey("key_0590").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0590: %d", got)
	}
	if got := e.shardForKey("key_0591").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0591: %d", got)
	}
	if got := e.shardForKey("key_0592").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0592: %d", got)
	}
	if got := e.shardForKey("key_0593").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0593: %d", got)
	}
	if got := e.shardForKey("key_0594").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0594: %d", got)
	}
	if got := e.shardForKey("key_0595").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0595: %d", got)
	}
	if got := e.shardForKey("key_0596").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0596: %d", got)
	}
	if got := e.shardForKey("key_0597").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0597: %d", got)
	}
	if got := e.shardForKey("key_0598").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0598: %d", got)
	}
	if got := e.shardForKey("key_0599").id; got < 0 || got >= shardCount {
		t.Fatalf("bad shard for key_0599: %d", got)
	}
}

func TestCompressionWorks(t *testing.T) {
	src := bytes.Repeat([]byte("xml-record-1234567890"), 200)
	cmp, err := compressZlib(src)
	if err != nil {
		t.Fatal(err)
	}
	if len(cmp) == 0 {
		t.Fatal("empty compressed data")
	}
	if len(cmp) >= len(src) {
		t.Fatalf("expected compression, got %d >= %d", len(cmp), len(src))
	}
}

func TestOpenStorageFileCreatesHeader(t *testing.T) {
	d := t.TempDir()
	p := filepath.Join(d, "node_0.lib")
	f, h, err := openStorageFile(p, libMagic)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	if h.Magic != libMagic || h.Version != version || h.LastOffset != headerSize {
		t.Fatalf("bad header: %#v", h)
	}
}

func TestAppendAdvancesOffsets(t *testing.T) {
	d := t.TempDir()
	s, err := openShard(d, 0)
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = s.libFile.Close(); _ = s.bagFile.Close() }()
	off1, l1, err := s.append("k1", "string", []byte("abc"))
	if err != nil {
		t.Fatal(err)
	}
	off2, _, err := s.append("k2", "binary", []byte("defghijkl"))
	if err != nil {
		t.Fatal(err)
	}
	if off2 <= off1 {
		t.Fatalf("offset did not advance: %d <= %d", off2, off1)
	}
	if l1 == 0 {
		t.Fatal("expected non-zero bag length")
	}
	if s.libHeader.EntryCount != 2 || s.bagHeader.EntryCount != 2 {
		t.Fatal("entry counters incorrect")
	}
}

func TestRoutingCase_000(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0000").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0000").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_001(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0001").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0001").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_002(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0002").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0002").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_003(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0003").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0003").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_004(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0004").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0004").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_005(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0005").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0005").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_006(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0006").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0006").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_007(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0007").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0007").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_008(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0008").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0008").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_009(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0009").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0009").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_010(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0010").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0010").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_011(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0011").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0011").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_012(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0012").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0012").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_013(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0013").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0013").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_014(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0014").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0014").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_015(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0015").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0015").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_016(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0016").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0016").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_017(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0017").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0017").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_018(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0018").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0018").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_019(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0019").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0019").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_020(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0020").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0020").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_021(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0021").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0021").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_022(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0022").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0022").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_023(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0023").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0023").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_024(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0024").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0024").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_025(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0025").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0025").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_026(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0026").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0026").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_027(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0027").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0027").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_028(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0028").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0028").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_029(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0029").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0029").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_030(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0030").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0030").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_031(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0031").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0031").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_032(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0032").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0032").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_033(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0033").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0033").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_034(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0034").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0034").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_035(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0035").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0035").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_036(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0036").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0036").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_037(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0037").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0037").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_038(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0038").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0038").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_039(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0039").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0039").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_040(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0040").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0040").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_041(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0041").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0041").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_042(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0042").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0042").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_043(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0043").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0043").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_044(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0044").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0044").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_045(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0045").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0045").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_046(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0046").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0046").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_047(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0047").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0047").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_048(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0048").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0048").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_049(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0049").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0049").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_050(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0050").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0050").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_051(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0051").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0051").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_052(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0052").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0052").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_053(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0053").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0053").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_054(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0054").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0054").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_055(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0055").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0055").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_056(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0056").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0056").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_057(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0057").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0057").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_058(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0058").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0058").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_059(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0059").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0059").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_060(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0060").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0060").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_061(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0061").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0061").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_062(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0062").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0062").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_063(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0063").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0063").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_064(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0064").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0064").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_065(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0065").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0065").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_066(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0066").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0066").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_067(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0067").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0067").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_068(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0068").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0068").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_069(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0069").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0069").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_070(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0070").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0070").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_071(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0071").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0071").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_072(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0072").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0072").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_073(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0073").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0073").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_074(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0074").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0074").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_075(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0075").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0075").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_076(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0076").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0076").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_077(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0077").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0077").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_078(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0078").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0078").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_079(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0079").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0079").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_080(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0080").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0080").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_081(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0081").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0081").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_082(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0082").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0082").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_083(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0083").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0083").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_084(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0084").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0084").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_085(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0085").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0085").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_086(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0086").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0086").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_087(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0087").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0087").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_088(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0088").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0088").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_089(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0089").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0089").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_090(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0090").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0090").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_091(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0091").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0091").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_092(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0092").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0092").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_093(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0093").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0093").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_094(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0094").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0094").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_095(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0095").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0095").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_096(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0096").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0096").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_097(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0097").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0097").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_098(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0098").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0098").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_099(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0099").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0099").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_100(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0100").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0100").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_101(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0101").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0101").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_102(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0102").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0102").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_103(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0103").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0103").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_104(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0104").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0104").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_105(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0105").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0105").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_106(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0106").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0106").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_107(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0107").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0107").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_108(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0108").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0108").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_109(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0109").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0109").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_110(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0110").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0110").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_111(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0111").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0111").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_112(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0112").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0112").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_113(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0113").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0113").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_114(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0114").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0114").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_115(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0115").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0115").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_116(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0116").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0116").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_117(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0117").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0117").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_118(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0118").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0118").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_119(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0119").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0119").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_120(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0120").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0120").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_121(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0121").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0121").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_122(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0122").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0122").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_123(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0123").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0123").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_124(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0124").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0124").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_125(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0125").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0125").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_126(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0126").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0126").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_127(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0127").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0127").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_128(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0128").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0128").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_129(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0129").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0129").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_130(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0130").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0130").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_131(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0131").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0131").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_132(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0132").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0132").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_133(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0133").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0133").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_134(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0134").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0134").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_135(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0135").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0135").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_136(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0136").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0136").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_137(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0137").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0137").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_138(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0138").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0138").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_139(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0139").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0139").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_140(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0140").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0140").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_141(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0141").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0141").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_142(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0142").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0142").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_143(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0143").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0143").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_144(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0144").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0144").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_145(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0145").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0145").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_146(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0146").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0146").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_147(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0147").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0147").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_148(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0148").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0148").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_149(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0149").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0149").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_150(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0150").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0150").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_151(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0151").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0151").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_152(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0152").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0152").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_153(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0153").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0153").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_154(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0154").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0154").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_155(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0155").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0155").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_156(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0156").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0156").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_157(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0157").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0157").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_158(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0158").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0158").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_159(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0159").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0159").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_160(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0160").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0160").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_161(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0161").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0161").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_162(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0162").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0162").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_163(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0163").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0163").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_164(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0164").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0164").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_165(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0165").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0165").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_166(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0166").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0166").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_167(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0167").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0167").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_168(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0168").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0168").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_169(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0169").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0169").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_170(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0170").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0170").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_171(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0171").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0171").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_172(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0172").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0172").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_173(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0173").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0173").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_174(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0174").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0174").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_175(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0175").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0175").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_176(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0176").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0176").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_177(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0177").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0177").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_178(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0178").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0178").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_179(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0179").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0179").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_180(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0180").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0180").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_181(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0181").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0181").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_182(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0182").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0182").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_183(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0183").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0183").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_184(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0184").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0184").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_185(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0185").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0185").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_186(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0186").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0186").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_187(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0187").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0187").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_188(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0188").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0188").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_189(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0189").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0189").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_190(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0190").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0190").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_191(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0191").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0191").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_192(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0192").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0192").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_193(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0193").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0193").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_194(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0194").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0194").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_195(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0195").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0195").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_196(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0196").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0196").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_197(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0197").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0197").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_198(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0198").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0198").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_199(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0199").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0199").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_200(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0200").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0200").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_201(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0201").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0201").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_202(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0202").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0202").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_203(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0203").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0203").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_204(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0204").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0204").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_205(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0205").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0205").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_206(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0206").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0206").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_207(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0207").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0207").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_208(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0208").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0208").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_209(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0209").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0209").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_210(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0210").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0210").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_211(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0211").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0211").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_212(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0212").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0212").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_213(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0213").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0213").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_214(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0214").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0214").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_215(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0215").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0215").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_216(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0216").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0216").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_217(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0217").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0217").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_218(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0218").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0218").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_219(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0219").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0219").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_220(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0220").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0220").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_221(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0221").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0221").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_222(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0222").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0222").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_223(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0223").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0223").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_224(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0224").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0224").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_225(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0225").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0225").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_226(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0226").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0226").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_227(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0227").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0227").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_228(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0228").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0228").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_229(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0229").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0229").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_230(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0230").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0230").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_231(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0231").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0231").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_232(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0232").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0232").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_233(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0233").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0233").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_234(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0234").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0234").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_235(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0235").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0235").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_236(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0236").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0236").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_237(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0237").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0237").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_238(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0238").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0238").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_239(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0239").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0239").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_240(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0240").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0240").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_241(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0241").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0241").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_242(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0242").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0242").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_243(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0243").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0243").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_244(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0244").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0244").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_245(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0245").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0245").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_246(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0246").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0246").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_247(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0247").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0247").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_248(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0248").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0248").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}

func TestRoutingCase_249(t *testing.T) {
	e := &engine{}
	for i := 0; i < shardCount; i++ {
		e.shards[i] = &shard{id: i}
	}
	got := e.shardForKey("key_0249").id
	if got < 0 || got >= shardCount {
		t.Fatalf("out of range: %d", got)
	}
	got2 := e.shardForKey("key_0249").id
	if got != got2 {
		t.Fatalf("non deterministic: %d %d", got, got2)
	}
}
