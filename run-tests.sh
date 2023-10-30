#!/bin/bash

set -e

OAREPO_VERSION=${OAREPO_VERSION:-11}
OAREPO_VERSION_MAX=$((OAREPO_VERSION+1))

if [ -d .venv-builder ] ; then
    rm -rf .venv-builder
fi

rm -rf .venv-builder

python3 -m venv .venv-builder
.venv-builder/bin/pip install -U setuptools pip wheel
.venv-builder/bin/pip install -e .

BUILDER=.venv-builder/bin/oarepo-compile-model

if [ -d built_tests ] ; then
    rm -rf built_tests
fi

mkdir built_tests

${BUILDER} tests/article.yaml --output-directory built_tests/article -vvv

rm -rf .venv-tests
python3 -m venv .venv-tests

source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install "oarepo>=$OAREPO_VERSION,<$OAREPO_VERSION_MAX"
pip install -e 'built_tests/article[tests]'
pip install pytest-invenio

pytest tests