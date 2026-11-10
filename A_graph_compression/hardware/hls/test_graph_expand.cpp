#include "graph_expand.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static void read_words(std::ifstream &f, uint32_t *p, size_t count) {
    f.read(reinterpret_cast<char *>(p), count*sizeof(uint32_t));
    if (!f) throw std::runtime_error("Truncated test input");
}
static void eof(std::ifstream &f) {
    if (f.peek()!=std::ifstream::traits_type::eof()) throw std::runtime_error("Extra input bytes");
}
int main(int argc, char **argv) {
    try {
        if(argc!=2)throw std::runtime_error("Usage: test_graph_expand manifest.txt");
        std::ifstream manifest(argv[1]);
        if(!manifest)throw std::runtime_error("Cannot read test manifest");
        std::string image_path, config_path, case_path;
        unsigned cases=0;
        while(manifest>>image_path>>config_path>>case_path) {
            std::vector<uint32_t> image(IMAGE_DEPTH,0), config(CFG_WORDS,0), requests(MAX_REQUESTS,0);
            std::vector<uint32_t> output(OUTPUT_DEPTH,0xdecafbad), result(RESULT_DEPTH,0xdecafbad);
            std::ifstream cf(config_path, std::ios::binary), im(image_path, std::ios::binary), tf(case_path, std::ios::binary);
            if(!cf || !im || !tf)throw std::runtime_error("Cannot read fixture");
            read_words(cf,config.data(),CFG_WORDS);eof(cf);
            if(config[IMAGE_WORDS]>IMAGE_DEPTH)throw std::runtime_error("Image too large");
            read_words(im,image.data(),config[IMAGE_WORDS]);eof(im);
            uint32_t h[4];read_words(tf,h,4);
            uint32_t n=h[0],capacity=h[1],expected_written=h[2],expected_failed=h[3];
            if(n>MAX_REQUESTS || capacity>OUTPUT_DEPTH || expected_written>capacity/8)throw std::runtime_error("Invalid fixture size");
            std::vector<uint32_t> expected_result(n*3), expected_output(expected_written*8);
            read_words(tf,requests.data(),n);read_words(tf,expected_result.data(),n*3);
            read_words(tf,expected_output.data(),expected_written*8);eof(tf);
            uint32_t written=0,failed=0;
            graph_expand(image.data(),config.data(),requests.data(),output.data(),result.data(),n,capacity,written,failed);
            if(written!=expected_written || failed!=expected_failed)throw std::runtime_error("Result counters differ: "+case_path);
            if(!std::equal(expected_result.begin(),expected_result.end(),result.begin()))throw std::runtime_error("Status/start/degree differs: "+case_path);
            if(!std::equal(expected_output.begin(),expected_output.end(),output.begin()))throw std::runtime_error("Edge/PIP/direction/property differs: "+case_path);
            for(size_t i=expected_output.size();i<output.size();i++)if(output[i]!=0xdecafbad)throw std::runtime_error("Output written beyond successful records");
            for(size_t i=n*3;i<result.size();i++)if(result[i]!=0xdecafbad)throw std::runtime_error("Result written beyond request batch");
            std::cout<<"CASE_PASS "<<case_path<<" requests="<<n<<" records="<<written<<" failed="<<failed<<std::endl;
            cases++;
        }
        if(!manifest.eof() || !cases)throw std::runtime_error("Empty or malformed manifest");
        std::cout<<"GRAPH_EXPAND_PASS cases="<<cases<<std::endl;
        return 0;
    } catch(const std::exception &e) {std::cerr<<"TEST_FAIL "<<e.what()<<std::endl;return 1;}
}
