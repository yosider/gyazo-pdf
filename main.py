import argparse
import os
from io import BytesIO
from pathlib import Path

import pyperclip
from dotenv import load_dotenv
from gyazo import Api
from pdf2image import convert_from_path
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Convert PDF pages to images and upload them to Gyazo.")
parser.add_argument("--pdf", type=str, default="", help="The name of the PDF file to convert")
parser.add_argument("--dpi", type=int, default=300, help="The DPI of the output image")
parser.add_argument("--first", type=int, default=1, help="The first page to convert")
parser.add_argument("--last", type=int, default=None, help="The last page to convert")
args = parser.parse_args()

# load env: PDF_DIR, GYAZO_API_TOKEN
load_dotenv()

# PDF path
pdf_dir = Path(os.environ.get("PDF_DIR"))
if args.pdf != "":
    path = pdf_dir / args.pdf / ".pdf"
else:
    # get the latest pdf file in PDF_DIR
    pdfs = list(pdf_dir.glob("*.pdf"))
    if len(pdfs) == 0:
        raise FileNotFoundError(f"No PDF files found in {str(pdf_dir)}.")
    path = max(pdfs, key=os.path.getctime)
    print(f"Latest PDF file: {path.name}")

last_page_str = "the last page" if args.last is None else f"p.{args.last}"
print(f"Converting from p.{args.first} to {last_page_str}...")
images = convert_from_path(
    pdf_path=path,
    dpi=args.dpi,
    first_page=args.first,
    last_page=args.last,
)

client = Api(access_token=os.environ.get("GYAZO_API_TOKEN"))

urls = []
for i, image in enumerate(tqdm(images, desc="uploading...")):
    with BytesIO() as img_byte_arr:
        # save image to byte array
        image.save(img_byte_arr, format="PNG")
        img_byte_data = img_byte_arr.getvalue()

        # upload to Gyazo
        res = client.upload_image(img_byte_data)
        url = res.url.replace("i.gyazo.com", "gyazo.com").replace(".png", "")
        urls.append(url)

# copy to clipboard
"""
[url 1]
[url 2]
...
[url N]

"""
pyperclip.copy("[" + "]\n[".join(urls) + "]\n")
