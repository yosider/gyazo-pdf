# Gyazo PDF
A Python script to convert PDF pages to images and upload them to Gyazo.  
The URLs of the uploaded images are copied to the clipboard.

## Prerequisites
- Python 3.x
- A Gyazo account and API token

## Installation
1. Clone the repository
```bash
git clone https://github.com/yosider/gyazo-pdf.git
cd pdf-to-gyazo
```

2. Install required packages
```bash
pip install -r requirements.txt
```

## Usage
Create a `.env` file in the same directory with `main.py` and set your Gyazo API token and the directory where your PDFs are stored.
```bash:.env
GYAZO_API_TOKEN=...
PDF_DIR=...
```

Add the following function to your `.bashrc` or `.zshrc`.  
```bash:.bashrc
gp() {
    python /path/to/main.py "$1"
}
```
You can simply use `gp <pdf name>` to run the script.  
You can replace "gp" with any name you prefer.
