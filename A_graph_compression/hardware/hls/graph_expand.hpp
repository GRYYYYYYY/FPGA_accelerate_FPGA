#pragma once
#include <stdint.h>
enum GraphConfig { MODE, NODE_BASE, NODE_COUNT, TILE_BASE, TILE_COUNT,
    GRID_BASE, GRID_COUNT, ALIAS_BASE, ALIAS_COUNT, INSTANCE_BASE, INSTANCE_COUNT,
    TPL_BASE, TPL_COUNT, RULE_BASE, RULE_COUNT, REMOVE_BASE, REMOVE_COUNT,
    ADD_BASE, ADD_COUNT, PATCH_BASE, PATCH_COUNT, CSR_OFF_BASE, CSR_OFF_COUNT,
    CSR_EDGE_BASE, CSR_EDGE_COUNT, STRING_COUNT, ATTR_COUNT, IMAGE_WORDS, CFG_WORDS=32 };
enum { MAX_DEGREE=1024, MAX_REQUESTS=65536, IMAGE_DEPTH=2097152,
       OUTPUT_DEPTH=1048576, RESULT_DEPTH=3*MAX_REQUESTS };
// Host must validate AGRAPH01 and descriptor bounds before enqueueing a batch.
// Each result is [output record start, degree, status]: 0 success, 1 unknown
// adjacency, 2 degree/output capacity, 3 invalid mapping, 4 invalid request/config.
extern "C" void graph_expand(const uint32_t image[IMAGE_DEPTH],
    const uint32_t config[CFG_WORDS], const uint32_t requests[MAX_REQUESTS],
    uint32_t output[OUTPUT_DEPTH], uint32_t result[RESULT_DEPTH],
    uint32_t request_count, uint32_t output_capacity_words,
    uint32_t &written_records, uint32_t &failed_requests);
