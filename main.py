import os
import shutil
import argparse
from pathlib import Path

import pyperclip
from dotenv import load_dotenv
from pdf2image import convert_from_path
from gyazo import Api
from tqdm import tqdm


parser = argparse.ArgumentParser(description="Convert PDF pages to images and upload them to Gyazo.")
parser.add_argument("pdf", type=str, help="The name of the PDF file to convert")
args = parser.parse_args()

# load env: PDF_DIR, GYAZO_API_TOKEN
load_dotenv()

images = convert_from_path(os.environ.get("PDF_DIR") + args.pdf + ".pdf")

# directory for images
img_dir = Path(Path.home() / "__tmp")
img_dir.mkdir()

# gyazo
client = Api(access_token=os.environ.get("GYAZO_API_TOKEN"))

# upload
urls = []
for i, image in tqdm(enumerate(images)):
    img_path = img_dir / f"page_{i}.png"
    image.save(img_path)

    with open(img_path, "rb") as f:
        url = client.upload_image(f).url.replace("i.gyazo.com", "gyazo.com").replace(".png", "")
        urls.append(url)

# copy to clipboard in the format of:
# [url1]
# [url2]
# ...
pyperclip.copy("[" + "]\n[".join(urls) + "]\n")
shutil.rmtree(img_dir)
