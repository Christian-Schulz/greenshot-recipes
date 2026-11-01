# CLI Apply Template & Annotation

Adds a dark badge with **REVIEWED: <today's date>** to the bottom right corner of an image file and saves the result
next to it as `<name>-with_annotation.png`. The new file name is printed, so scripts can pick it up.

## Use it

```
greenshot-cli -r annotate --file=C:\Pictures\example1.png
```

| Argument | Meaning |
|---|---|
| `file` | The image to stamp (required) |

## Allows

Reads the image you name and writes the new file in the same folder.
