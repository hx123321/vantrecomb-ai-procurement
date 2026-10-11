#!/usr/bin/env python3
"""Package the existing plugin against a parent-verified ChatGPT cloud app."""
import argparse
import json
from pathlib import Path
import re
import zipfile


def build(source, app_id, output):
    # Syntax is a guard, not proof of registration; verify ID/endpoint in ChatGPT.
    if not re.fullmatch(r"plugin_asdk_app_[A-Za-z0-9]+", app_id):
        raise ValueError("Provide the actual plugin_asdk_app ID from the cloud connection")
    if any(word in app_id.lower() for word in ("example", "placeholder", "replace", "fake")):
        raise ValueError("Placeholder app IDs cannot be packaged")
    source = source.resolve()
    output = output.resolve()
    if output.is_relative_to(source):
        raise ValueError("Write the archive outside the plugin source directory")
    manifest = json.loads((source / "plugin.json").read_text(encoding="utf-8"))
    manifest["extensions"]["com.openai"]["apps"] = "./.app.json"
    overlay = {key: manifest[key] for key in ("name", "version", "description", "author")}
    overlay.update(skills="./skills", apps="./.app.json",
                   interface=manifest["extensions"]["com.openai"]["interface"])
    binding = {"apps": {"vantrecomb-procurement": {"id": app_id}}}
    # Only runtime directories are bundled, not docs, builders, local sessions or MCP routes.
    runtime = []
    for directory in ("skills", "assets"):
        for path in sorted((source / directory).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink cannot be packaged: {path.relative_to(source)}")
            if not path.is_file():
                continue
            if path.name.startswith(".env") or "__pycache__" in path.parts or path.suffix == ".pyc":
                raise ValueError(f"Local configuration/cache cannot be packaged: {path.relative_to(source)}")
            runtime.append((path.relative_to(source).as_posix(), path.read_bytes()))
    if not any(name.endswith("/SKILL.md") for name, _ in runtime):
        raise ValueError("No bundled skill found")
    files = {name: (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
             for name, value in (("plugin.json", manifest),
                                 (".codex-plugin/plugin.json", overlay),
                                 (".app.json", binding))}
    files.update(runtime)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(manifest["name"] + "/" + name, data)
    print(f"Created {output} ({len(files)} runtime files). OAuth and host verification remain required.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", required=True, help="Parent-verified cloud connection ID; no defaults")
    parser.add_argument("--output", required=True, type=Path, help="New archive outside plugin source")
    args = parser.parse_args()
    try:
        build(Path(__file__).resolve().parents[1] / "plugins" / "vantrecomb-procurement-plugin", args.app_id, args.output)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
