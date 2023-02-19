import copy
from oarepo_model_builder.datatypes import ObjectDataType
from oarepo_model_builder.stack import ReplaceElement
from oarepo_model_builder.validation import InvalidModelException

from oarepo_model_builder_relations.datatypes import RelationSchema
from marshmallow import fields
from oarepo_model_builder.utils.deepmerge import deepmerge


class VocabularyDataType(ObjectDataType):
    model_type = "vocabulary"

    def mapping(self, **extras):
        ret = super().mapping(**extras)
        return ret

    def model_schema(self, **extras):
        data = copy.deepcopy(self.definition)
        data.pop("type", None)
        fields = data.pop("keys", ["id", "title"])
        vocabulary_type = data.pop("vocabulary-type", None)
        vocabulary_imports = data.pop("imports", [])
        model = data.pop("model", "vocabularies")
        vocabulary_class = data.pop("class", None)
        name = data.pop("name", None)

        schema_prefix = data.pop("schema-prefix", None)
        relation_classes = data.pop("relation-classes", None)
        relation_class = data.pop("relation-class", None)
        pid_field = data.pop("pid-field", None)
        flatten = data.pop("flatten", None)
        marshmallow = data.pop("marshmallow", {})

        if not pid_field:
            if not vocabulary_class:
                if not vocabulary_type:
                    raise InvalidModelException(
                        "{self.stack.path}: If vocabulary class is not specified, need to have vocabulary-type"
                    )
                pid_field = f'Vocabulary.pid.with_type_ctx("{vocabulary_type}")'
                vocabulary_imports.append(
                    {"import": "invenio_vocabularies.records.api.Vocabulary"}
                )
                if "imports" not in marshmallow:
                    marshmallow["imports"] = []
                marshmallow["imports"].append(
                    {"import": "invenio_vocabularies.services.schema.i18n_strings"}
                )
            else:
                if vocabulary_type:
                    raise InvalidModelException(
                        "{self.stack.path}: Can not have both vocabulary class and type specified"
                    )
                pid_field = f"{vocabulary_class}.pid"

        relation_settings = {
            "type": "relation",
            "model": model,
            "keys": fields,
            "imports": vocabulary_imports,
            "pid-field": pid_field,
            "name": name,
            "schema-prefix": schema_prefix,
            "relation-classes": relation_classes,
            "relation-class": relation_class,
            "flatten": flatten,
            "marshmallow": marshmallow,
        }

        raise ReplaceElement(
            {
                self.key: deepmerge(
                    data,
                    {k: v for k, v in relation_settings.items() if v is not None},
                )
            }
        )

    class ModelSchema(RelationSchema, ObjectDataType.ModelSchema):
        vocabulary_type = fields.String(
            attribute="vocabulary-type", data_key="vocabulary-type", required=False
        )
        model = fields.String(required=False)


class TaxonomyDataType(VocabularyDataType):
    model_type = "taxonomy"

    def model_schema(self, **extras):
        keys = list(self.definition.get("keys", []))

        def has_key(fields, field_name):
            for fld in fields:
                if isinstance(fld, str):
                    if field_name == fld:
                        return True
                elif isinstance(fld, dict):
                    if field_name == fld.get("key", None):
                        return True
            return False

        if not has_key(keys, "id"):
            keys.append("id")
        if not has_key(keys, "title"):
            keys.append("title")
        if not has_key(keys, "hierarchy"):
            keys.append(
                {
                    "key": "hierarchy",
                    "model": {
                        "type": "object",
                        "properties": {
                            "parent": {"type": "keyword"},
                            "level": {"type": "integer"},
                            "title": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "propertyNames": {"pattern": "^[a-z]{2}$"},
                                    "additionalProperties": {"type": "str"},
                                    "mapping": {"dynamic": True},
                                    "marshmallow": {"field": "i18n_strings"},
                                },
                            },
                            "ancestors": {
                                "type": "array",
                                "items": {"type": "keyword"},
                            },
                        },
                    },
                }
            )
        raise ReplaceElement(
            {
                self.key: {
                    **self.definition,
                    "type": "vocabulary",
                    "keys": list(keys),
                }
            }
        )


DATATYPES = [VocabularyDataType, TaxonomyDataType]
