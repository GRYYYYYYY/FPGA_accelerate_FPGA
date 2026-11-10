cmake_minimum_required(VERSION 3.13)
project(rwroute_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Match Java float semantics: 32-bit floats, no fast-math reassociation.
# MEASURED NEGATIVE (2026-07-11): -march=native (even with -ffp-contract=off) still shifts FP code
# paths somewhere -- mcml totalPIPs 123241->123780, RS8 134970->134833 = bit-identity broken. The
# invariant is non-negotiable; baseline x86-64 codegen stays. (Bulk-loop SIMD would need per-function
# target attributes on integer/memcpy-only helpers.)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fno-fast-math")
add_compile_options($<$<COMPILE_LANGUAGE:CXX>:-Wall> $<$<COMPILE_LANGUAGE:CXX>:-Wextra> $<$<COMPILE_LANGUAGE:CXX>:-Wno-unused-parameter>)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# ---- CUDA detection (shared by the standalone router AND the JNI library) ----
# Both the GPU coarse-grid bbox solver (gpu_bbox.cu) and the GPU detailed-routing engine
# (gpu_route.cu) compile only when a CUDA toolkit is found; otherwise the routers build CPU-only and
# fall back to the CPU paths. Putting CUDA on the standalone target too lets us iterate the GPU
# router on .rrt files without the JNI/Java round-trip.
find_program(RW_NVCC nvcc PATHS /usr/local/cuda/bin /usr/local/cuda-12.4/bin /usr/local/cuda-12/bin /usr/local/cuda-11.8/bin)
set(RW_CUDA OFF)
if(RW_NVCC)
  set(CMAKE_CUDA_COMPILER ${RW_NVCC})
  enable_language(CUDA)
  get_filename_component(RW_CUDA_BIN ${RW_NVCC} DIRECTORY)
  get_filename_component(RW_CUDA_HOME ${RW_CUDA_BIN} DIRECTORY)
  set(RW_CUDA ON)
  set(RW_CUDA_SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/src/gpu_bbox.cu
    ${CMAKE_CURRENT_SOURCE_DIR}/src/gpu_route.cu)
  message(STATUS "CUDA enabled (${RW_NVCC}, sm_86): gpu_bbox.cu + gpu_route.cu")
else()
  message(WARNING "nvcc not found; building CPU-only (no GPU bbox / GPU routing)")
endif()

# Attach the CUDA sources + toolkit to a target (no-op when CUDA is unavailable).
function(rw_attach_cuda tgt)
  if(RW_CUDA)
    target_sources(${tgt} PRIVATE ${RW_CUDA_SRCS})
    set_target_properties(${tgt} PROPERTIES CUDA_ARCHITECTURES "86"
      BUILD_RPATH ${RW_CUDA_HOME}/lib64 INSTALL_RPATH ${RW_CUDA_HOME}/lib64)
    target_compile_definitions(${tgt} PRIVATE WITH_CUDA)
    target_include_directories(${tgt} PRIVATE ${RW_CUDA_HOME}/include)
    target_link_directories(${tgt} PRIVATE ${RW_CUDA_HOME}/lib64)
    target_link_libraries(${tgt} cudart)
  endif()
endfunction()

# ---- Part 1: custom .rrt/.result router (standalone; also the GPU-router dev harness) ----
add_executable(rwroute_cpp ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp)
target_link_libraries(rwroute_cpp Threads::Threads)
rw_attach_cuda(rwroute_cpp)

# ---- JNI shared library: same router core, in-process entry (no disk, single JVM) ----
set(JDK_HOME "/home/zhlin/jdk11" CACHE PATH "JDK with jni.h")
if(EXISTS "${JDK_HOME}/include/jni.h")
  add_library(RWRouteCppJni SHARED ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp)
  target_compile_definitions(RWRouteCppJni PRIVATE WITH_JNI)
  target_include_directories(RWRouteCppJni PRIVATE
    ${JDK_HOME}/include ${JDK_HOME}/include/linux)
  target_link_libraries(RWRouteCppJni Threads::Threads)
  rw_attach_cuda(RWRouteCppJni)
else()
  message(WARNING "jni.h not found at ${JDK_HOME}; skipping RWRouteCppJni")
endif()

# ---- Part 2: FPGAIF (Cap'n Proto) front-end ----
# Cap'n Proto from the isolated conda env (capnproto 0.9.1).
set(CAPNP_ENV "/home/zhlin/miniconda3/envs/fpgaif" CACHE PATH "conda env with capnproto")
if(EXISTS "${CAPNP_ENV}/lib/libcapnp.so")
  file(GLOB CAPNP_GEN ${CMAKE_CURRENT_SOURCE_DIR}/capnp_gen/interchange/*.c++)
  file(GLOB FPGAIF_SRC ${CMAKE_CURRENT_SOURCE_DIR}/fpgaif/*.cpp)
  add_executable(rwroute_fpgaif ${FPGAIF_SRC} ${CAPNP_GEN})
  target_include_directories(rwroute_fpgaif PRIVATE
    ${CAPNP_ENV}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/capnp_gen/interchange
    ${CMAKE_CURRENT_SOURCE_DIR}/include)
  target_link_directories(rwroute_fpgaif PRIVATE ${CAPNP_ENV}/lib)
  target_link_libraries(rwroute_fpgaif capnp kj)
  set_target_properties(rwroute_fpgaif PROPERTIES
    BUILD_RPATH ${CAPNP_ENV}/lib
    INSTALL_RPATH ${CAPNP_ENV}/lib)
else()
  message(WARNING "Cap'n Proto not found at ${CAPNP_ENV}; skipping rwroute_fpgaif")
endif()
