from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput


class VocabulariesSetupCfgBuilder(OutputBuilder):
    TYPE = "vocabularies_setup_cfg"

    def finish(self):
        super().finish()

        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")
        output.add_dependency("oarepo-vocabularies", ">=2.0.0")
