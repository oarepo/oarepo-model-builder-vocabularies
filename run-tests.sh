#!/bin/bash

set -e

if ! [ -d .venv ] ; then
    python3 -m venv .venv
    .venv/bin/pip install -U setuptools pip wheel
    .venv/bin/pip install -e .
fi

BUILDER=.venv/bin/oarepo-compile-model

if ! [ -f tests/article/setup.cfg ] ; then
    test -d tests/article && rm -rf tests/article
    ${BUILDER} tests/article.yaml --output-directory tests/article -vvv
fi

if ! [ -d .venv-tests ] ; then
    python3 -m venv .venv-tests
fi

source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install pyyaml opensearch-dsl 
pip install -e tests/article
pip install pytest-invenio

pytest tests