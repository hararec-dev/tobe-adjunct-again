from pathlib import Path
from string import Template


class TemplateLoader:
    def __init__(self, template_dir="src/templates"):
        self.template_dir = Path(template_dir)

    def load_template(self):
        template_path = self.template_dir / "message.txt"

        with open(template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def load_subject_template(self):
        with open(self.template_dir / "subject.txt", "r", encoding="utf-8") as f:
            # Para el asunto fijo, creamos un Template pero no necesitamos sustitución
            class FixedTemplate:
                def __init__(self, template_string):
                    self.template = template_string.strip()

                def substitute(self, **kwargs):
                    return self.template

            return FixedTemplate(f.read())
