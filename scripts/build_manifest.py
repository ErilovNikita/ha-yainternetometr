import json
import tomllib
from pathlib import Path
from jinja2 import Template

ROOT = Path.cwd()
PYP_FILE = ROOT / "pyproject.toml"
TEMPLATE_FILE = ROOT / "templates/manifest.json.j2"
INTEGRATION_PATH = ROOT / "custom_components/yainternetometr"
OUTPUT_FILE = INTEGRATION_PATH / "manifest.json"

def main():
    with PYP_FILE.open("rb") as f:
        conf = tomllib.load(f)

    project = conf["project"]
    hacs = conf.get("tool", {}).get("hacs", {})

    with TEMPLATE_FILE.open("r", encoding="utf-8") as f:
        template = Template(f.read())

    manifest = template.render(
        domain = hacs["domain"],
        name = hacs["russian_name"],
        version = project["version"],
        documentation = project.get("urls", {}).get("Documentation"),
        issue_tracker = project.get("urls", {}).get("Issues"),
        requirements = project.get("dependencies", []),
        codeowner = hacs.get("codeowner", []),
        config_flow = hacs.get("config_flow", False)
    )

    manifest_json = json.loads(manifest)

    INTEGRATION_PATH.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2, ensure_ascii=False)

    print(f"✔ Generated manifest.json for {hacs['domain']}-(v{project['version']}) at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()