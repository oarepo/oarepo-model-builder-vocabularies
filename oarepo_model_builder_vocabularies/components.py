from oarepo_model_builder.datatypes.components import ObjectFacetsComponent
from oarepo_model_builder.datatypes.components.facets import FacetDefinition

from oarepo_model_builder_vocabularies.datatypes import VocabularyDataType


class VocabularyDataTypeComponent(ObjectFacetsComponent):
    eligible_datatypes = [VocabularyDataType]

    def build_facet_definition(
        self,
        datatype,
        facet_definition: FacetDefinition,
    ):
        # do not build facet definition for children of this component
        return []


COMPONENTS = [VocabularyDataTypeComponent]
