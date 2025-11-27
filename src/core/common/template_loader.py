from pathlib import Path
from string import Template


class TemplateLoader:
    def __init__(self, template_dir="src/templates"):
        self.template_dir = Path(template_dir)

    def load_template(self):
        template_path = self.template_dir / f"message.txt"

        with open(template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def load_subject_template(self):
        with open(self.template_dir / "subject.txt", "r", encoding="utf-8") as f:
            return Template(f.read())
