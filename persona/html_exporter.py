
import os
from jinja2 import Environment, FileSystemLoader

class HTMLExporter:
    """
    Exports persona data to a styled HTML file using a Jinja2 template.
    """

    def __init__(self, template_dir="persona/templates"):
        """Initializes the Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

    def export(self, persona_data, output_path):
        """
        Renders the persona data with the template and saves it to a file.
        """
        template = self.env.get_template("persona_template.html")
        html_content = template.render(persona=persona_data)

        #  output directory 
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)