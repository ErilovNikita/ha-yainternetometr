import json
import tomllib
from pathlib import Path
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
PYP_FILE = ROOT / "pyproject.toml"

def main():
    with PYP_FILE.open("rb") as f:
        conf = tomllib.load(f)

    project = conf["project"]
    ha = conf.get("tool", {}).get("hacs", {})
    domain = ha["domain"]

    template_file = ROOT / "templates" / "hacs.json.j2"
    output_file = ROOT / "hacs.json"

    with template_file.open("r", encoding="utf-8") as f:
        template = Template(f.read())

    manifest = template.render(
        name = project["name"],
        homeassistant = ha.get("homeassistant", {}),
        country = ha.get("country", {})
    )

    manifest_json = json.loads(manifest)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2, ensure_ascii=False)

    print(f"✔ Generated hacs.json for {domain} (v{project['version']})")


if __name__ == "__main__":
    main()