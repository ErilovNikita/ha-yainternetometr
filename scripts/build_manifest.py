import json
import tomllib
from pathlib import Path
from jinja2 import Template

ROOT = Path.cwd()
PYP_FILE = ROOT / "pyproject.toml"

def main():
    with PYP_FILE.open("rb") as f:
        conf = tomllib.load(f)

    project = conf["project"]
    ha = conf.get("tool", {}).get("hacs", {})

    domain = ha["domain"]
    integration_dir = ROOT / "custom_components" / domain

    template_file = ROOT / "templates" / "manifest.json.j2"
    output_file = integration_dir / "manifest.json"

    with template_file.open("r", encoding="utf-8") as f:
        template = Template(f.read())

    manifest = template.render(
        domain = domain,
        name = project["name"],
        version = project["version"],
        documentation = project.get("urls", {}).get("Documentation"),
        issue_tracker = project.get("urls", {}).get("Issues"),
        requirements = project.get("dependencies", []),
        codeowner = ha.get("codeowner", []),
        config_flow = ha.get("config_flow", False)
    )

    manifest_json = json.loads(manifest)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2, ensure_ascii=False)

    print(f"✔ Generated manifest.json for {domain} (v{project['version']})")


if __name__ == "__main__":
    main()