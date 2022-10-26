#! /bin/bash

# ubuntu [18.04 ; 20.04 ; 22.04]
# debian [9 ; 10]

#export CM_CACHE="--no-cache"

#export CM_OS_NAME="debian"
#export CM_OS_VERSION="10"

export CM_OS_NAME="ubuntu"
export CM_OS_VERSION="20.04"

export CM_ML_ENGINE="onnxruntime"
export CM_ML_ENGINE_VERSION="1.12.1"

docker build -f cm-mlperf-inference-retinanet-ubuntu-cpu.Dockerfile \
   -t ckrepo/cm-mlperf-inference-retinanet-ubuntu-cpu:${CM_OS_NAME}-${CM_OS_VERSION} \
   --build-arg cm_os_name=${CM_OS_NAME} \
   --build-arg cm_os_version=${CM_OS_VERSION} \
   --build-arg cm_version="" \
   --build-arg cm_automation_repo="octoml@ck" \
   --build-arg cm_automation_checkout="" \
   --build-arg cm_python_version="3.10.7" \
   --build-arg cm_cmake_version="3.24.2" \
   --build-arg cm_mlperf_inference_loadgen_version="" \
   --build-arg cm_mlperf_inference_src_tags="_octoml" \
   --build-arg cm_mlperf_inference_src_version="" \
   --build-arg cm_ml_engine=${CM_ML_ENGINE} \
   --build-arg cm_ml_engine_version=${CM_ML_ENGINE_VERSION} \
  ${CM_CACHE} .
