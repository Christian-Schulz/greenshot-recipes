# Contributing a recipe

## A recipe folder

```
recipes/<id>/
  recipe.gsrecipe.json   the recipe, exactly the file Greenshot imports
  catalog.json           what the catalog needs to list it (not part of the recipe)
  README.md              what it does, how to use it, what it asks to allow
  CHANGELOG.md           optional
  images/                optional screenshots (png, jpg, gif, webp)
```

The easiest way to write a recipe is Greenshot's recipe editor; the format is described in
[capture-recipes.md](https://github.com/greenshot/greenshot/blob/main/docs/vNext/capture-recipes.md) and
[recipe.schema.json](https://github.com/greenshot/greenshot/blob/main/docs/vNext/recipe.schema.json).

## Rules

The check on every pull request enforces these:

- The recipe matches Greenshot's recipe schema.
- The folder name is the recipe `id`: lower case letters, digits and `_`. Ids starting with `recipe_` or `ext_` belong
  to Greenshot's own recipes.
- `authors` names everyone who wrote it, each with their GitHub login; a new recipe names the person who submits it.
  A change adds authors, it never removes one.
- `copyright` (e.g. `"Copyright (c) 2026 Jane Doe"`) and `"license": "MIT"` are in the file.
- No fixed hotkeys: a `Hotkey` trigger takes its key from a `Hotkey` option, so every user picks their own:

  ```json
  "options": [ { "key": "hotkey", "type": "Hotkey", "default": "Ctrl + Shift + D", "label": "Hotkey" } ],
  "triggers": [ { "triggerType": "Hotkey", "parameters": { "Hotkey": "${option.hotkey}" } } ]
  ```

- `catalog.json` has `version`, `minGreenshot` and a one line `summary` (see [catalog.schema.json](catalog.schema.json));
  every change of the recipe file raises `version`.
- Nothing else in the folder.

Run the same check locally (Python 3.9+, `pip install jsonschema`):

```
python tools/catalog.py check --schema path/to/greenshot/docs/vNext/recipe.schema.json --base origin/main
```

## Review

A maintainer reviews every pull request; recipes that run programs or send data to a server get a closer look. Say in
the README what the recipe asks to allow and why.

## License of contributions

By opening a pull request you agree that your contribution is published under the [MIT license](LICENSE) of this
repository, with you named in `authors` and `copyright`.
