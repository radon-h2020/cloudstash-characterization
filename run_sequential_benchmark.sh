#!/bin/bash

###
### Log message boilerplate
###

# terminal espace codes for a rainy day
NONE='\033[00m'
RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
WHITE='\033[01;37m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

# for displaying messages that indicate the start of a process
function start_msg {
  echo -e "${YELLOW}${BOLD}--> $1${NONE}"
}

# for displaying progress
function progress_msg {
  echo -e "${PURPLE}-->${NONE} ${BOLD}$1${NONE}"
}

# for errers
function error_msg {
 echo -e "${RED}${BOLD}--> $1${NONE}"
}

# general messages
function msg {
  echo -e "${BOLD}$1${NONE}"
}

# success message
function success_msg {
echo -e "${BOLD}${GREEN}--> $1${NONE}"
}

###
### Script vars
###

# exit if anything has a non-zero exitcode
set -e

# create a timestamp
timestamp=$(date +"%H-%M-%S_%m-%d_%Y")

# name of container
container_name="sequential-benchmark-$timestamp"

# where are log files stored
log_dir="logs"
# TODO change
# log_dir="/home/ubuntu/logs"

# create log dir if it does not exist
[ ! -d "$log_dir" ] && progress_msg "Creating logs directory ..." && mkdir -p "$log_dir"

# logfile for container
logfile="$log_dir/$container_name.log"

# what benchmark to run
benchmark="sequential_upload"

# how many artefacts to upload in the benchmark
number_of_artefacts=10
# TODO change
# number_of_artefacts=100000

# create the docker cmd as a string that we can run in the background, but still pipe stdout to logfile
cmd="
docker run \
    --rm \
    --name $container_name \
    -v /home/zander/eficode/radon/cloudstash-characterization/EC2/secrets/.aws:/home/alpine/.aws:ro \
    -v /home/zander/eficode/radon/cloudstash/serverless:/home/alpine/serverless \
    -v /home/zander/eficode/radon/cloudstash-characterization:/home/alpine/cloudstash-characterization \
    cc:latest \
    $benchmark $number_of_artefacts \
    > $logfile
"
# TODO change away from dev
# docker run --rm -it \
    # -v /home/ubuntu/.aws:/home/alpine/.aws:ro \
    # -v /home/ubuntu/cloudstash/serverless:/home/alpine/serverless \
    # docker.pkg.github.com/radon-h2020/cloudstash-characterization/cloudstash-benchmarker:main

###
### Running the benchmark container
###

# TODO remove
error_msg "NOTE THAT THIS SCRIPT IS RUNNING IN DEVELOPMENT MODE"

start_msg "Now running benchmark: $benchmark"
progress_msg "Number of artefacts that will be uploaded: $number_of_artefacts"
progress_msg "Benchmark will run in container: $container_name"
progress_msg "Benchmark logs will be written to: $logfile"

# run the benchmark container as a background process
bash -c "$cmd" &

success_msg "Container started."
progress_msg "This may take some time to finish ..."

# if you pass --tail to the script, you will follow the logfile
[[ $* = *--tail* ]] && progress_msg "Following $logfile, press Ctrl-c to exit." && tail -F "$logfile"
