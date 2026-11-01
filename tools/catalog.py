#!/usr/bin/env python3
# Copyright (c) 2026 the Greenshot recipe catalog authors
# SPDX-License-Identifier: MIT
"""Checks the recipe catalog and builds its index.

  catalog.py check --schema recipe.schema.json [--base origin/main] [--pr-author login]
  catalog.py index --repository greenshot/greenshot-recipes --commit <sha> --out index.json

Needs Python 3.9+ and jsonschema (pip install jsonschema).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import jsonschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES = os.path.join(ROOT, "recipes")
RECIPE_FILE = "recipe.gsrecipe.json"
CATALOG_FILE = "catalog.json"
REQUIRED_FILES = (RECIPE_FILE, CATALOG_FILE, "README.md")
OPTIONAL_FILES = ("CHANGELOG.md",)
IMAGE_FOLDER = "images"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
# Greenshot's own recipes and automatic steps use these; a recipe with the same id would replace a built-in one
RESERVED_PREFIXES = ("recipe_", "ext_")
LICENSE = "MIT"
OPTION_REFERENCE = re.compile(r"^\$\{option\.([A-Za-z][A-Za-z0-9_]*)\}$")


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def recipe_folders():
    if not os.path.isdir(RECIPES):
        return []
    return sorted(name for name in os.listdir(RECIPES) if os.path.isdir(os.path.join(RECIPES, name)))


def parse_version(text):
    return tuple(int(part) for part in text.split("-")[0].split("."))


def git_show(ref, path):
    """The content of a file at a git ref, None when it doesn't exist there."""
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def check_folder(folder, recipe_validator, catalog_validator, errors):
    path = os.path.join(RECIPES, folder)
    where = f"recipes/{folder}"

    for name in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(path, name)):
            errors.append(f"{where}: {name} is missing")
    for name in os.listdir(path):
        full = os.path.join(path, name)
        if name in REQUIRED_FILES or name in OPTIONAL_FILES:
            continue
        if name == IMAGE_FOLDER and os.path.isdir(full):
            for image in os.listdir(full):
                if not image.lower().endswith(IMAGE_EXTENSIONS):
                    errors.append(f"{where}/{IMAGE_FOLDER}/{image}: only images ({', '.join(IMAGE_EXTENSIONS)}) belong here")
            continue
        errors.append(f"{where}/{name}: not expected, a recipe folder holds {', '.join(REQUIRED_FILES + OPTIONAL_FILES)} and {IMAGE_FOLDER}/")

    recipe = catalog = None
    try:
        recipe = load_json(os.path.join(path, RECIPE_FILE))
    except (OSError, ValueError) as error:
        errors.append(f"{where}/{RECIPE_FILE}: can't be read: {error}")
    try:
        catalog = load_json(os.path.join(path, CATALOG_FILE))
    except (OSError, ValueError) as error:
        errors.append(f"{where}/{CATALOG_FILE}: can't be read: {error}")

    if recipe is not None:
        for error in sorted(recipe_validator.iter_errors(recipe), key=lambda e: list(e.absolute_path)):
            location = "/".join(str(part) for part in error.absolute_path) or "(file)"
            errors.append(f"{where}/{RECIPE_FILE}: {location}: {error.message}")
        check_recipe_rules(where, folder, recipe, errors)
    if catalog is not None:
        for error in catalog_validator.iter_errors(catalog):
            location = "/".join(str(part) for part in error.absolute_path) or "(file)"
            errors.append(f"{where}/{CATALOG_FILE}: {location}: {error.message}")
    return recipe, catalog


def check_recipe_rules(where, folder, recipe, errors):
    if not isinstance(recipe, dict):
        return
    recipe_id = recipe.get("id")
    if recipe_id != folder:
        errors.append(f"{where}: the recipe id '{recipe_id}' must be the folder name")
    if not isinstance(recipe_id, str) or not ID_PATTERN.match(recipe_id):
        errors.append(f"{where}: the id must be lower case letters, digits and _ and start with a letter")
    elif recipe_id.startswith(RESERVED_PREFIXES):
        errors.append(f"{where}: ids starting with {' or '.join(RESERVED_PREFIXES)} belong to Greenshot's own recipes")

    authors = recipe.get("authors") or []
    if not authors:
        errors.append(f"{where}: 'authors' is missing, name at least one author")
    for author in authors:
        if isinstance(author, dict) and not author.get("github"):
            errors.append(f"{where}: author '{author.get('name')}' needs a 'github' login")
    if not recipe.get("copyright"):
        errors.append(f"{where}: 'copyright' is missing, e.g. \"Copyright (c) 2026 Jane Doe\"")
    if recipe.get("license") != LICENSE:
        errors.append(f"{where}: 'license' must be \"{LICENSE}\", all catalog recipes are {LICENSE}")

    # A hotkey is the user's choice: catalog recipes offer it as a Hotkey option, never fixed in the file
    hotkey_options = {option.get("key") for option in recipe.get("options") or [] if isinstance(option, dict) and option.get("type") == "Hotkey"}
    for index, trigger in enumerate(recipe.get("triggers") or []):
        if not isinstance(trigger, dict) or trigger.get("triggerType") != "Hotkey":
            continue
        value = (trigger.get("parameters") or {}).get("Hotkey")
        match = OPTION_REFERENCE.match(value) if isinstance(value, str) else None
        if not match or match.group(1) not in hotkey_options:
            errors.append(f"{where}: triggers/{index}: a Hotkey trigger takes its hotkey from a Hotkey option, "
                          f"e.g. \"Hotkey\": \"${{option.hotkey}}\" with an option of type Hotkey")


def github_logins(recipe):
    return {author.get("github", "").lower() for author in (recipe or {}).get("authors") or [] if isinstance(author, dict) and author.get("github")}


def check_against_base(folder, recipe, catalog, base, pr_author, errors):
    where = f"recipes/{folder}"
    old_recipe_bytes = git_show(base, f"recipes/{folder}/{RECIPE_FILE}")
    if old_recipe_bytes is None:
        if pr_author and recipe is not None and pr_author.lower() not in github_logins(recipe):
            errors.append(f"{where}: a new recipe names its submitter in 'authors' (github: {pr_author})")
        return
    with open(os.path.join(RECIPES, folder, RECIPE_FILE), "rb") as file:
        if file.read() == old_recipe_bytes:
            return
    old_recipe = json.loads(old_recipe_bytes)
    missing = github_logins(old_recipe) - github_logins(recipe)
    if missing:
        errors.append(f"{where}: a change adds authors, it doesn't remove them (missing: {', '.join(sorted(missing))})")
    old_catalog_bytes = git_show(base, f"recipes/{folder}/{CATALOG_FILE}")
    if old_catalog_bytes is None or catalog is None:
        return
    try:
        old_version = parse_version(json.loads(old_catalog_bytes)["version"])
        new_version = parse_version(catalog["version"])
    except (KeyError, ValueError):
        return
    if new_version <= old_version:
        errors.append(f"{where}: the recipe changed, so 'version' in {CATALOG_FILE} needs to go up")


def command_check(arguments):
    recipe_validator = jsonschema.Draft7Validator(load_json(arguments.schema))
    catalog_validator = jsonschema.Draft7Validator(load_json(os.path.join(ROOT, "catalog.schema.json")))
    errors = []
    folders = recipe_folders()
    for folder in folders:
        recipe, catalog = check_folder(folder, recipe_validator, catalog_validator, errors)
        if arguments.base:
            check_against_base(folder, recipe, catalog, arguments.base, arguments.pr_author, errors)
    for error in errors:
        print(f"::error::{error}" if os.environ.get("GITHUB_ACTIONS") else error)
    print(f"{len(folders)} recipe(s) checked, {len(errors)} error(s)")
    return 1 if errors else 0


def command_index(arguments):
    base_url = f"https://raw.githubusercontent.com/{arguments.repository}/{arguments.commit}/recipes"
    entries = []
    for folder in recipe_folders():
        recipe_path = os.path.join(RECIPES, folder, RECIPE_FILE)
        with open(recipe_path, "rb") as file:
            recipe_bytes = file.read()
        recipe = json.loads(recipe_bytes)
        catalog = load_json(os.path.join(RECIPES, folder, CATALOG_FILE))
        entries.append({
            "id": recipe["id"],
            "version": catalog["version"],
            "name": recipe["name"],
            "summary": catalog["summary"],
            "kind": recipe.get("kind", "recipe"),
            "authors": recipe.get("authors", []),
            "license": recipe.get("license"),
            "minGreenshot": catalog["minGreenshot"],
            "requires": recipe.get("requires") or [],
            "tags": catalog.get("tags", []),
            "sha256": hashlib.sha256(recipe_bytes).hexdigest(),
            "url": f"{base_url}/{folder}/{RECIPE_FILE}",
            "readme": f"{base_url}/{folder}/README.md",
        })
    index = {
        "indexVersion": 1,
        "repository": arguments.repository,
        "commit": arguments.commit,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "recipes": entries,
    }
    with open(arguments.out, "w", encoding="utf-8", newline="\n") as file:
        json.dump(index, file, indent=2, ensure_ascii=False)
        file.write("\n")
    print(f"{arguments.out}: {len(entries)} recipe(s)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check every recipe folder")
    check.add_argument("--schema", required=True, help="Greenshot's recipe.schema.json")
    check.add_argument("--base", help="git ref to compare with (version bump, authors)")
    check.add_argument("--pr-author", help="GitHub login of the pull request's author")
    check.set_defaults(run=command_check)
    index = commands.add_parser("index", help="write index.json")
    index.add_argument("--repository", required=True, help="owner/name of this repository")
    index.add_argument("--commit", required=True, help="the commit the download links point to")
    index.add_argument("--out", default="index.json")
    index.set_defaults(run=command_index)
    arguments = parser.parse_args()
    return arguments.run(arguments)


if __name__ == "__main__":
    sys.exit(main())
