# Gyazo PDF
A Python script to convert PDF pages to images and upload them to Gyazo.  
The URLs of the uploaded images are copied to the clipboard.

## Prerequisites
- Python >= 3.8
- Gyazo account and API token

## Installation
Clone the repository and install
```bash
git clone https://github.com/yosider/gyazo-pdf.git
cd gyazo-pdf
pip install .
```

## Usage
Create a config file at `~/.config/gyazo_pdf/config.yaml` and set your Gyazo API token and the directory where your PDFs are stored.
```yaml
GYAZO_API_TOKEN: ...
PDF_DIR: /path/to/dir  # The script searches pdf files in this directory
```

Then run the command:
```bash
gp example.pdf
```
or you can omit the file name to upload the latest PDF file in the directory:
```bash
gp
```
