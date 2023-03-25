from oarepo_model_builder.validation import InvalidModelException

from marshmallow import fields
from oarepo_model_builder_relations.datatypes import RelationDataType
import munch
from oarepo_model_builder.utils.hyphen_munch import HyphenMunch


class VocabularyDataType(RelationDataType):
    model_type = "vocabulary"

    def prepare(self, context):
        vocabulary_type = self.definition.pop("vocabulary-type", None)
        vocabulary_class = self.definition.pop("class", None)

        vocabulary_imports = self.definition.setdefault("imports", [])
        self.definition.setdefault("model", "vocabularies")
        self.definition.setdefault(
            "keys", ["id", "title", {"key": "type.id", "target": "type"}]
        )
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

        self.definition["type"] = "relation"
        self.definition["pid-field"] = pid_field
        super().prepare(context)

    class ModelSchema(RelationDataType.ModelSchema):
        vocabulary_type = fields.String(
            attribute="vocabulary-type", data_key="vocabulary-type", required=False
        )
        model = fields.String(required=False)


class TaxonomyDataType(VocabularyDataType):
    model_type = "taxonomy"

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
        if not has_key(keys, "type.id"):
            keys.append({"key": "type.id", "target": "type"})
        if not has_key(keys, "hierarchy"):
            keys.append(
                {
                    "key": "hierarchy",
                    "model": {
                        "type": "object",
                        "marshmallow": {
                            "schema-class": "oarepo_vocabularies.services.schemas.HierarchySchema",
                            "generate": False,
                            "imports": [
                                {
                                    "import": "oarepo_vocabularies.services.schemas.HierarchySchema"
                                }
                            ],
                        },
                        "ui": {
                            "marshmallow": {
                                "schema-class": "oarepo_vocabularies.services.ui_schemas.HierarchyUISchema",
                                "generate": False,
                            },
                            "imports": [
                                {
                                    "import": "oarepo_vocabularies.services.ui_schemas.HierarchyUISchema"
                                }
                            ],
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
                        },
                    },
                }
            )
        self.definition["type"] = type
        self.definition["keys"] = munch.munchify(list(keys), HyphenMunch)
        super().prepare(context)


DATATYPES = [VocabularyDataType, TaxonomyDataType]
