#!/bin/bash

set -e

rm -rf .venv

python3 -m venv .venv
.venv/bin/pip install -U setuptools pip wheel
.venv/bin/pip install -e .

BUILDER=.venv/bin/oarepo-compile-model

if [ -d built_tests ] ; then
    rm -rf built_tests
fi

mkdir built_tests

${BUILDER} tests/article.yaml --output-directory built_tests/article -vvv

rm -rf .venv-tests
python3 -m venv .venv-tests

source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install cairocffi
pip install pyyaml opensearch-dsl 
pip install oarepo
pip install built_tests/article
pip install pytest-invenio
pip install 'oarepo-runtime>=1.1.5'
pip install 'oarepo-vocabularies>=1.0.4'
pip install tqdm

pytest tests