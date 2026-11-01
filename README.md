# Greenshot recipes

Recipes for [Greenshot](https://getgreenshot.org): small JSON files that tell Greenshot what to do with a capture, for
example add a watermark, convert a file, or run your own tool after a capture.

Recipes come with Greenshot 1.4, currently in beta.

## Use a recipe

Each folder under [`recipes/`](recipes) is one recipe. Download its `recipe.gsrecipe.json` and import it in Greenshot's
recipe manager. Greenshot shows what the recipe does and what it needs your permission for (running a program, sending
data to a server, writing files) before anything runs.

## Add or change a recipe

See [CONTRIBUTING.md](CONTRIBUTING.md). Every recipe is checked automatically and reviewed by a maintainer before it is
merged.

## Report a problem

Open an issue: "Bug in a recipe" or "Recipe request". Security problems: see [SECURITY.md](SECURITY.md).

## License

All recipes are under the [MIT license](LICENSE). Each recipe names its authors and copyright inside the file, so the
credit stays with every copy.

Recipes describe what Greenshot should do; Greenshot itself is GPL and lives in
[greenshot/greenshot](https://github.com/greenshot/greenshot).
