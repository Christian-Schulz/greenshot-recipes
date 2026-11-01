# CLI Image Format Converter

Loads an image file, converts it to the format you ask for and saves it next to the original with the new extension.
The new file name is printed.

## Use it

```
greenshot-cli -r convert --file=C:\Pictures\photo.png --format=webp
```

| Argument | Meaning |
|---|---|
| `file` | The image to convert (required) |
| `format` | `png`, `jpg`, `webp`, `bmp`, `gif` or `tiff` (default `jpg`) |

## Allows

Reads the image you name and writes the converted file in the same folder.
