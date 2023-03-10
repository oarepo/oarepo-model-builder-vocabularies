#!/bin/bash

set -e

rm -rf .venv

python3 -m venv .venv
.venv/bin/pip install -U setuptools pip wheel
.venv/bin/pip install -e .

BUILDER=.venv/bin/oarepo-compile-model

rm -rf tests/article

${BUILDER} tests/article.yaml --output-directory tests/article -vvv

rm -rf .venv-tests
python3 -m venv .venv-tests

source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install pyyaml opensearch-dsl 
pip install -e tests/article
pip install pytest-invenio
pip install 'oarepo-runtime>=1.1.5'
pip install 'oarepo-vocabularies>=1.0.4'

pytest tests