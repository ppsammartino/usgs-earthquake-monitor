#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

source /app/utils/utils__common.bash

TEMP_OUTPUT_FILE="formatting.tmp"

function at_exit {
  rm -f $TEMP_OUTPUT_FILE
}

trap at_exit EXIT

assert_tool ruff
task "Fixing formatting with ${BOLD}ruff${RESET}.."
script --quiet --return --command "ruff format ./api 2>&1" /dev/null | log 'ruff format'
result=${PIPESTATUS[0]}

if [ $result -ne 0 ]
then
  error "Something went wrong during execution.."
  exit 1
else
  success "Done."
fi
