# CLI QR Code & Barcode Extractor

Loads an image file, finds QR codes and barcodes in it and prints what they say, so a script can use it.

## Needs

The ZXing plugin (QR codes and barcodes), which comes with Greenshot.

## Use it

```
greenshot-cli -r qr --file=C:\Pictures\invoice.png
```

| Argument | Meaning |
|---|---|
| `file` | The image with the code (required) |

## Allows

Reads the image you name.
