#!/bin/bash

name=$1
timeout=10
sleep=0

IS_RUNNING=0
IS_RESTARTING=1
IS_EXITED=2
IS_DEAD=3

function get_state() {
	echo "Start"
	state=$(sudo docker inspect -f '{{ .State.Status }}' ${name})
	return_code=$?
	if [ ! ${return_code} -eq 0 ]; then
           exit 1
        fi
        if [[ "${state}" == "running" ]]; then
           echo 0
           return ${IS_RUNNING}
        elif [[ "${state}" == "restarting" ]]; then
           echo 1
           return ${IS_RESTARTING}
        elif [[ "${state}" == "exited" ]]; then
           echo 2	
           return ${IS_EXITED}
        elif [[ "${state}" == "dead" ]]; then
           echo 3 	
           return ${IS_DEAD}
        else
           return 999
        fi
}

function wait_for_container() {
	while [ "$sleep" -ne 3 ]; do
	  get_state
	  state=$?
	  if [ ${state} -eq 0 ]; then
            echo "Container running"
          else
            echo "State of container $(sudo docker inspect -f '{{ .State.Status }}' ${name})"
            exit 1
          fi
            sleep=$(( $sleep + 1 ))
	    sleep ${timeout}
	done
	exit 0
}

if [ -z "$name" ]; then
  exit 1
else
  echo "Run"	
  wait_for_container
fi