# Gyazo PDF
A Python script to convert PDF pages to images and upload them to Gyazo.  
The URLs of the uploaded images are copied to the clipboard.

## Prerequisites
- [Gyazo](https://gyazo.com/) account and API token
- [pipx](https://pipx.pypa.io/) or [uv](https://docs.astral.sh/uv/)

## Installation
```bash
# Using pipx
pipx install gyazo-pdf

# Or using uv
uv tool install gyazo-pdf
```

## Configuration
Create a config file at `~/.config/gyazo-pdf/config.yaml`:
```yaml
GYAZO_API_TOKEN: your_token_here
PDF_DIR: /path/to/pdf/directory
```

## Usage
```bash
# Upload a specific PDF
gp filename  # or filename.pdf

# Upload the latest PDF in the configured directory
gp
```
