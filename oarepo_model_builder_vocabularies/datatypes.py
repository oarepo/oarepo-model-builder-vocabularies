import marshmallow as ma
from marshmallow import fields
from oarepo_model_builder.datatypes.components.model.utils import array_contains_value
from oarepo_model_builder.datatypes.datatypes import DataType
from oarepo_model_builder.validation import InvalidModelException
from oarepo_model_builder_relations.datatypes import RelationDataType


class VocabularyDataType(RelationDataType):
    model_type = "vocabulary"
    facets = {
        "facet-class": "VocabularyFacet",
        "imports": [{"import": "oarepo_vocabularies.services.facets.VocabularyFacet"}],
    }

    class ModelSchema(RelationDataType.ModelSchema):
        vocabulary_type = ma.fields.String(
            attribute="vocabulary-type", data_key="vocabulary-type"
        )

    def prepare(self, context):
        vocabulary_type = self.definition.get("vocabulary-type", None)
        vocabulary_class = self.definition.pop("class", None)

        vocabulary_imports = self.definition.setdefault("imports", [])
        self.definition.setdefault("model", "vocabularies")
        keys = list(self.definition.setdefault("keys", ["id", "title"]))
        self.definition.setdefault("marshmallow", {})
        self.definition.setdefault("ui", {}).setdefault("marshmallow", {})
        self.definition["ui"].setdefault("detail", "vocabulary_item")
        self.definition["ui"].setdefault("edit", "vocabulary_item")
        pid_field = self.definition.get("pid-field", None)

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
            else:
                if vocabulary_type:
                    raise InvalidModelException(
                        "{self.stack.path}: Can not have both vocabulary class and type specified"
                    )
                pid_field = f"{vocabulary_class}.pid"

        # self.definition["type"] = "relation"
        self.definition["pid-field"] = pid_field

        # set up vocabulary argument to facets
        facets = self.definition.setdefault("facets", {})
        facets_args = facets.setdefault("args", [])
        vocabulary_attr = f"vocabulary={repr(vocabulary_type)}"
        if not array_contains_value(facets_args, vocabulary_attr):
            facets_args.append(vocabulary_attr)

        transformed_keys = []
        for key in keys:
            if isinstance(key, str) and key.startswith("props."):
                transformed_keys.append(
                    {"key": key, "model": {"type": "keyword"}, "target": key[6:]}
                )
            else:
                transformed_keys.append(key)
        self.definition["keys"] = transformed_keys
        super().prepare(context)

    def get_facet(self, stack, parent_path):
        if not stack:
            # we are the facet, unlike normal container, for which a facet is not generated,
            # we need to generate it -> calling direct data type
            return DataType.get_facet(self, stack, parent_path)

        # do not return any facets for children
        return []

    def _get_facet_definition(
        self, stack, facet_class, facet_name, path, path_suffix, label, serialized_args
    ):
        # the container's implementation counts on generating facets for children and not self,
        # so bypassing it and calling direct data type
        vocabulary_type = self.definition.get("vocabulary-type", None)
        if vocabulary_type:
            serialized_args += ", "
            serialized_args += f'vocabulary="{vocabulary_type}"'
        return DataType._get_facet_definition(
            self,
            stack,
            facet_class,
            facet_name,
            path,
            path_suffix,
            label,
            serialized_args,
        )

    class ModelSchema(RelationDataType.ModelSchema):
        vocabulary_type = fields.String(
            attribute="vocabulary-type", data_key="vocabulary-type", required=False
        )
        model = fields.String(required=False)


class TaxonomyDataType(VocabularyDataType):
    model_type = "taxonomy"
    facets = {
        "facet-class": "HierarchyVocabularyFacet",
        "imports": [
            {"import": "oarepo_vocabularies.services.facets.HierarchyVocabularyFacet"}
        ],
    }

    def prepare(self, context):
        keys = list(self.definition.get("keys", []))
        self.definition.setdefault("ui", {}).setdefault("detail", "taxonomy_item")
        self.definition["ui"].setdefault("edit", "taxonomy_item")

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
                        "marshmallow": {
                            "class": "oarepo_vocabularies.services.schema.HierarchySchema",
                            "generate": False,
                            "imports": [
                                {
                                    "import": "oarepo_vocabularies.services.schema.HierarchySchema"
                                }
                            ],
                        },
                        "ui": {
                            "marshmallow": {
                                "class": "oarepo_vocabularies.services.ui_schema.HierarchyUISchema",
                                "generate": False,
                                "imports": [
                                    {
                                        "import": "oarepo_vocabularies.services.ui_schema.HierarchyUISchema"
                                    }
                                ],
                            },
                        },
                        "properties": {
                            "parent": {"type": "keyword"},
                            "level": {"type": "integer"},
                            "title": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "propertyNames": {"pattern": "^[a-z]{2}$"},
                                    "additionalProperties": {"type": "string"},
                                    "mapping": {"dynamic": True},
                                    "marshmallow": {"field": "i18n_strings"},
                                    "ui": {
                                        "marshmallow": {"field": "i18n_strings"},
                                    },
                                },
                            },
                            "ancestors": {
                                "type": "array",
                                "items": {"type": "keyword"},
                            },
                            "ancestors_or_self": {
                                "type": "array",
                                "items": {"type": "keyword"},
                            },
                        },
                    },
                }
            )
        self.definition["keys"] = list(keys)
        super().prepare(context)


DATATYPES = [VocabularyDataType, TaxonomyDataType]
