// Minimal little-endian binary reader for the custom .rrt bridge format.
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>

namespace com::xilinx::rapidwright::rwroute {

// Reads an entire file into memory and provides sequential little-endian decoding.
class BinReader {
public:
    explicit BinReader(const std::string& path) {
        FILE* f = std::fopen(path.c_str(), "rb");
        if (!f) throw std::runtime_error("BinReader: cannot open " + path);
        std::fseek(f, 0, SEEK_END);
        long sz = std::ftell(f);
        std::fseek(f, 0, SEEK_SET);
        buf_.resize(static_cast<size_t>(sz));
        if (sz > 0 && std::fread(buf_.data(), 1, static_cast<size_t>(sz), f) != static_cast<size_t>(sz)) {
            std::fclose(f);
            throw std::runtime_error("BinReader: short read on " + path);
        }
        std::fclose(f);
    }

    // Construct from an in-memory buffer (e.g. a JNI direct/byte[] problem) — no disk I/O.
    BinReader(const uint8_t* data, size_t n) : buf_(data, data + n) {}

    size_t pos() const { return pos_; }
    size_t size() const { return buf_.size(); }
    bool eof() const { return pos_ >= buf_.size(); }
    const uint8_t* data() const { return buf_.data(); }   // raw access for parallel section decoding
    void seek(size_t p) { pos_ = p; }

    uint8_t u8() { return readRaw<uint8_t>(); }
    int16_t i16() { return static_cast<int16_t>(readRaw<uint16_t>()); }
    uint16_t u16() { return readRaw<uint16_t>(); }
    int32_t i32() { return static_cast<int32_t>(readRaw<uint32_t>()); }
    uint32_t u32() { return readRaw<uint32_t>(); }
    int64_t i64() { return static_cast<int64_t>(readRaw<uint64_t>()); }

    float f32() {
        uint32_t v = readRaw<uint32_t>();
        float out;
        std::memcpy(&out, &v, sizeof(out));
        return out;
    }

    std::string str() {
        uint32_t n = u32();
        ensure(n);
        std::string s(reinterpret_cast<const char*>(buf_.data() + pos_), n);
        pos_ += n;
        return s;
    }

    void expectMagic(const char m[4]) {
        ensure(4);
        if (std::memcmp(buf_.data() + pos_, m, 4) != 0) {
            throw std::runtime_error("BinReader: bad magic");
        }
        pos_ += 4;
    }

private:
    template <typename T>
    T readRaw() {
        ensure(sizeof(T));
        T v;
        std::memcpy(&v, buf_.data() + pos_, sizeof(T));  // host assumed little-endian (x86_64)
        pos_ += sizeof(T);
        return v;
    }
    void ensure(size_t n) {
        if (pos_ + n > buf_.size()) throw std::runtime_error("BinReader: unexpected EOF");
    }

    std::vector<uint8_t> buf_;
    size_t pos_ = 0;
};

}  // namespace com::xilinx::rapidwright::rwroute
