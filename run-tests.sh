#!/bin/bash

set -e

PYTHON=${PYTHON:-python3.10}

OAREPO_VERSION=${OAREPO_VERSION:-12}

if [ -d .venv-builder ] ; then
    rm -rf .venv-builder
fi

rm -rf .venv-builder

${PYTHON} -m venv .venv-builder
.venv-builder/bin/pip install -U setuptools pip wheel
.venv-builder/bin/pip install -e .

BUILDER=.venv-builder/bin/oarepo-compile-model

if [ -d built_tests ] ; then
    rm -rf built_tests
fi

mkdir built_tests

${BUILDER} tests/article.yaml --output-directory built_tests/article -vvv

rm -rf .venv-tests
${PYTHON} -m venv .venv-tests

source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install "oarepo[tests]==${OAREPO_VERSION}.*"
pip install -e 'built_tests/article[tests]'

pytest tests