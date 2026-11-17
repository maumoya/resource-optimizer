#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# 2 MB of zeros, made here so the repo ships no binary file.
dd if=/dev/zero of=./old-project/build.bin bs=1000000 count=2 2>/dev/null
