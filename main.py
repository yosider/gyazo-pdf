import argparse
import os
from io import BytesIO

import pyperclip
from dotenv import load_dotenv
from gyazo import Api
from pdf2image import convert_from_path
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="Convert PDF pages to images and upload them to Gyazo."
)
parser.add_argument("pdf", type=str, help="The name of the PDF file to convert")
parser.add_argument("--dpi", type=int, default=300, help="The DPI of the output image")
parser.add_argument(
    "--first_page", type=int, default=1, help="The first page to convert"
)
parser.add_argument(
    "--last_page", type=int, default=None, help="The last page to convert"
)
args = parser.parse_args()

# load env: PDF_DIR, GYAZO_API_TOKEN
load_dotenv()

client = Api(access_token=os.environ.get("GYAZO_API_TOKEN"))

print("converting...")
images = convert_from_path(
    os.environ.get("PDF_DIR") + args.pdf + ".pdf",
    dpi=args.dpi,
    first_page=args.first_page,
    last_page=args.last_page,
)

urls = []
for i, image in enumerate(tqdm(images, desc="uploading...")):
    with BytesIO() as img_byte_arr:
        # save image to byte array
        image.save(img_byte_arr, format="PNG")
        img_byte_data = img_byte_arr.getvalue()

        # upload to Gyazo
        url = (
            client.upload_image(img_byte_data)
            .url.replace("i.gyazo.com", "gyazo.com")
            .replace(".png", "")
        )
        urls.append(url)

# copy to clipboard
"""
[url 1]
[url 2]
...
[url N]

"""
pyperclip.copy("[" + "]\n[".join(urls) + "]\n")
