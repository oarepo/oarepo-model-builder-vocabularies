black oarepo_model_builder_vocabularies tests --target-version py310
autoflake --in-place --remove-all-unused-imports --recursive oarepo_model_builder_vocabularies tests
isort oarepo_model_builder_vocabularies tests  --profile black
