#!/bin/bash

set -ex

rm -rf skupper

git clone https://github.com/skupperproject/skupper

(
    cd skupper

    make

    failed=0

    make test || failed=1

    go test -v -tags=integration ./test/integration/acceptance/custom/basic || failed=1

    if (( $failed == 1 )); then
        exit 1
    fi
)
