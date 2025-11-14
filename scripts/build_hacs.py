import json
import tomllib
from pathlib import Path
from jinja2 import Template

ROOT = Path.cwd()
PYP_FILE = ROOT / "pyproject.toml"
TEMPLATE_FILE = ROOT / "templates/hacs.json.j2"
INTEGRATION_PATH = ROOT / "custom_components/yainternetometr"
OUTPUT_FILE = INTEGRATION_PATH / "hacs.json"

def main():
    with PYP_FILE.open("rb") as f:
        conf = tomllib.load(f)

    project = conf["project"]
    hacs = conf.get("tool", {}).get("hacs", {})

    with TEMPLATE_FILE.open("r", encoding="utf-8") as f:
        template = Template(f.read())

    manifest = template.render(
        name = project["name"],
        homeassistant = hacs.get("homeassistant", {}),
        country = hacs.get("country", {})
    )

    manifest_json = json.loads(manifest)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2, ensure_ascii=False)

    print(f"✔ Generated hacs.json for {hacs['domain']} (v{project['version']})")


if __name__ == "__main__":
    main()