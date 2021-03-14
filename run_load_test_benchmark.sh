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
### sanity check
###

if [ ! "$USER" = "ubuntu" ] && [[ ! $* = *--local*  ]] ; then
    error_msg "You do not seem to be running on the server, use flag --local for runnig locally."
    exit 1
elif [ ! "$USER" = "ubuntu" ] && [[ $* = *--local*  ]] ; then
    progress_msg "Running script in local mode."
elif [ "$USER" = "ubuntu" ] && [[ $* = *--local*  ]] ; then
    msg "You seem to be trying to run in local mode on the server."
    exit 1
elif [ "$USER" = "ubuntu" ] && [[ ! $* = *--local*  ]] ; then
    msg "Running script in production mode."
fi

###
### Script vars
###

# exit if anything has a non-zero exitcode
set -e

# create a timestamp
timestamp=$(date +"%H-%M-%S_%m-%d_%Y")

if [[ $* = *--local* ]] ; then
    log_dir="logs"
    output_dir="output"
    artifacts_dir="artifacts"
    local_dir=$(pwd)
else
    log_dir="/home/ubuntu/logs"
    output_dir="/home/ubuntu/output"
    artifacts_dir="/home/ubuntu/artifacts"
fi

# create log dir if it does not exist
[ ! -d "$log_dir" ] && progress_msg "Creating logs directory ..." && mkdir -p "$log_dir"
[ ! -d "$output_dir" ] && progress_msg "Creating output directory ..." && mkdir -p "$output_dir"
[ ! -d "$artifacts_dir" ] && progress_msg "Creating artifacts directory ..." && mkdir -p "$artifacts_dir"

debug=""
verbose=""
reallyverbose=""
[[ $* = *--debug* ]] && progress_msg "Enabling debug prints" && debug="--debug"
[[ $* = *--verbose* ]] && progress_msg "Enabling verbose prints" && verbose="--verbose"
[[ $* = *--reallyverbose* ]] && progress_msg "Enabling really verbose prints" && reallyverbose="--reallyverbose"


# what benchmark to run
benchmark="load_test"

# how many artefacts to upload in the benchmark
# must be given as the first argument
number_of_artefacts=$1

# check that the first argument is an interger, and exit otherwise
# everything is strings in bash, so we use regex to make that the first
# argument can be matched to regex looking for an integer
check_number_reges="^[0-9]+$"
if ! [[ $number_of_artefacts =~ $check_number_reges ]] ; then
    error_msg "Error: First argument must be an integer."
    exit 1
fi

# name of container
container_name="$benchmark-$number_of_artefacts-$timestamp"

# logfile for container
logfile="$log_dir/$container_name.log"

docker_image="zanderhavgaard/cloudstash-characterization"
docker_tag="latest"

progress_msg "Pulling newest docker image ..."
docker pull "$docker_image:$docker_tag"

# create the docker cmd as a string that we can run in the background, but still pipe stdout to logfile
if [[ $* = *--local* ]] ; then
    cmd="
    docker run \
        --rm \
        --name $container_name \
        -v $local_dir/EC2/secrets/.aws:/home/alpine/.aws:ro \
        -v $local_dir/../cloudstash/serverless:/home/alpine/serverless \
        -v $local_dir:/home/alpine/cloudstash-characterization \
        -v $local_dir/artifacts:/home/alpine/artifacts \
        -v $local_dir/output:/home/alpine/output \
        $docker_image:$docker_tag \
        $debug $verbose $reallyverbose $benchmark $number_of_artefacts \
        > $logfile
    "
else
    cmd="
    docker run \
        --rm \
        --name $container_name \
        -v /home/ubuntu/.aws:/home/alpine/.aws:ro \
        -v /home/ubuntu/cloudstash/serverless:/home/alpine/serverless \
        -v /home/ubuntu/output:/home/alpine/output \
        -v /home/ubuntu/artifacts:/home/alpine/artifacts \
        $docker_image:$docker_tag \
        $debug $verbose $reallyverbose $benchmark $number_of_artefacts \
        > $logfile
    "
fi

###
### Running the benchmark container
###

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
