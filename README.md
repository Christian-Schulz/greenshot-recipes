# Greenshot recipes

Recipes for [Greenshot](https://getgreenshot.org): small JSON files that tell Greenshot what to do with a capture, for
example add a watermark, convert a file, or run your own tool after a capture.

Recipes come with Greenshot 1.4, currently in beta.

## Use a recipe

Pick a recipe on [getgreenshot.org/recipes](https://getgreenshot.org/recipes/?from=greenshot) and click "Install":
Greenshot downloads it from this catalog and shows what the recipe does, what it needs your permission for (running a
program, sending data to a server, writing files) and its settings before anything runs. You can also download a
folder's `recipe.gsrecipe.json` under [`recipes/`](recipes) and import it in Greenshot's recipe manager.

## How Greenshot trusts the catalog

Every merge that changes a recipe publishes a release with `index.json` (each recipe's version, SHA-256 and download
link pinned to the merge commit) and `index.json.sig`, its ECDSA P-256 signature. Greenshot checks the signature with
the public keys built into it, then the SHA-256 of the recipe file it downloads.

The private key is the repository secret `RECIPE_INDEX_SIGNING_KEY`. To make a key pair:

```
openssl ecparam -name prime256v1 -genkey -noout -out recipe-index.key.pem
openssl pkey -in recipe-index.key.pem -pubout -out recipe-index.pub.pem
```

The public key (base64 between the PEM lines) goes into `RecipeCatalogSignature.CatalogKeys` in Greenshot. Greenshot
knows two keys, so a second, offline key can take over without a Greenshot release in between.

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
