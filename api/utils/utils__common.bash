#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

export TERM=xterm

if which tput &>/dev/null
then
  RED=$(tput setaf 1)
  RED_BG=$(tput setab 1)
  GREEN=$(tput setaf 2)
  YELLOW=$(tput setaf 3)
  BLUE=$(tput setaf 4)
  MAGENTA=$(tput setaf 5)
  CYAN=$(tput setaf 6)
  RESET=$(tput sgr0)
  BOLD=$(tput bold)
else
  RED=""
  RED_BG=""
  GREEN=""
  YELLOW=""
  BLUE=""
  MAGENTA=""
  CYAN=""
  RESET=""
  BOLD=""
fi

function task {
  echo "| ${BOLD}${BLUE}>>${RESET} | $@"
}

function log {
  target=${1:-""}
  if [ -z "$target" ]
  then
    sed -e "s/^/| ${BOLD}..${RESET} | /" <&0
  else
    sed -e "s/^/| ${BOLD}..${RESET} | ${BOLD}${target}${RESET} | /" <&0
  fi
}

function success {
  echo "| ${BOLD}${GREEN}OK${RESET} | $@"
}

function error {
  echo "| ${BOLD}${RED}!!${RESET} | $@"
}

function assert_tool {
  tool=$1
  if ! pip freeze | grep -q $tool &>/dev/null
  then
    error "Tool not found: ${BOLD}${tool}${RESET}! Did you initialize the dev environment?"
    exit 1
  fi
}
