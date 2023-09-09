import argparse
import os
from io import BytesIO

import pyperclip
from dotenv import load_dotenv
from gyazo import Api
from pdf2image import convert_from_path
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Convert PDF pages to images and upload them to Gyazo.")
parser.add_argument("pdf", type=str, help="The name of the PDF file to convert")
args = parser.parse_args()

# load env: PDF_DIR, GYAZO_API_TOKEN
load_dotenv()

client = Api(access_token=os.environ.get("GYAZO_API_TOKEN"))

images = convert_from_path(os.environ.get("PDF_DIR") + args.pdf + ".pdf")

urls = []
for i, image in enumerate(tqdm(images)):
    with BytesIO() as img_byte_arr:
        # save image to byte array
        image.save(img_byte_arr, format="PNG")
        img_byte_data = img_byte_arr.getvalue()

        # upload to Gyazo
        url = client.upload_image(img_byte_data).url.replace("i.gyazo.com", "gyazo.com").replace(".png", "")
        urls.append(url)

# copy to clipboard
"""
[url 1]
[url 2]
...
[url N]

"""
pyperclip.copy("[" + "]\n[".join(urls) + "]\n")
