from pkg_resources import parse_version

from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput
from oarepo_model_builder.utils.verbose import log


class VocabulariesSetupCfgBuilder(OutputBuilder):
    TYPE = "vocabularies_setup_cfg"

    def finish(self):
        super().finish()

        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")
        output.add_dependency("invenio_vocabularies", ">=1.0.4")
