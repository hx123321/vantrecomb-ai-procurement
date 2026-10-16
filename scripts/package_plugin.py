#!/usr/bin/env python3
"""Package the existing plugin against a parent-verified ChatGPT cloud app."""
import argparse
import json
from pathlib import Path
import re
import zipfile


def runtime_files(source, directories):
    files = {}
    for directory in directories:
        for path in sorted((source / directory).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink cannot be packaged: {path.relative_to(source)}")
            if not path.is_file():
                continue
            if path.name.startswith(".env") or "__pycache__" in path.parts or path.suffix == ".pyc":
                raise ValueError(f"Local configuration/cache cannot be packaged: {path.relative_to(source)}")
            files[path.relative_to(source).as_posix()] = path.read_bytes()
    if not any(name.endswith("/SKILL.md") for name in files):
        raise ValueError("No bundled skill found")
    return files


def write_archive(source, output, name, files):
    output = output.resolve()
    if output.is_relative_to(source.resolve()):
        raise ValueError("Write the archive outside the plugin source directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(name + "/" + path, data)
    print(f"Created {output} ({len(files)} runtime files). Parent review and saved update remain required.")


def build(source, output):
    source = source.resolve()


    binding = json.loads((source / ".app.json").read_text(encoding="utf-8"))
    apps = binding.get("apps")
    if not isinstance(apps, dict) or len(apps) != 1:
        raise ValueError("Source must contain one verified cloud app binding")
    app = next(iter(apps.values()))
    app_id = app.get("id") if isinstance(app, dict) else None
    if not isinstance(app_id, str) or not re.fullmatch(r"asdk_app_[A-Za-z0-9]+", app_id):
        raise ValueError("Use the actual asdk_app ID from the cloud release's .app.json")
    if any(word in app_id.lower() for word in ("example", "placeholder", "replace", "fake")):
        raise ValueError("Placeholder app IDs cannot be packaged")
    manifest = json.loads((source / "plugin.json").read_text(encoding="utf-8"))
    manifest["extensions"]["com.openai"]["apps"] = "./.app.json"
    overlay = {key: manifest[key] for key in ("name", "version", "description", "author")}
    overlay.update(skills="./skills", apps="./.app.json",
                   interface=manifest["extensions"]["com.openai"]["interface"])
    files = {name: (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
             for name, value in (("plugin.json", manifest),
                                 (".codex-plugin/plugin.json", overlay),
                                 (".app.json", binding))}
    files.update(runtime_files(source, ("skills", "assets")))
    write_archive(source, output, manifest["name"], files)


def build_app_overlay(source, manifest_path, output):

    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("skills") != "./skills":
        raise ValueError("App overlay must load the bundled skills directory")
    files = {".codex-plugin/plugin.json": manifest_bytes}
    files.update(runtime_files(source, ("skills",)))

    write_archive(source, output, manifest["name"], files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New archive outside plugin source")
    parser.add_argument("--app-overlay-output", type=Path, help="Optional skills-only overlay for the verified TEST App plugin")
    args = parser.parse_args()
    try:
        project = Path(__file__).resolve().parents[1]
        source = project / "plugins" / "vantrecomb-procurement-plugin"
        build(source, args.output)
        if args.app_overlay_output:
            build_app_overlay(source, project / "overlays" / "vantrecomb-test" / ".codex-plugin" / "plugin.json", args.app_overlay_output)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
