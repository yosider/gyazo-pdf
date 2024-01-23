import argparse
import os
from io import BytesIO
from pathlib import Path

import pyperclip
import yaml
from gyazo import Api
from pdf2image import convert_from_path
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Convert PDF pages to images and upload them to Gyazo.")
parser.add_argument("--pdf", type=str, default="", help="The name of the PDF file to convert")
parser.add_argument("--dpi", type=int, default=300, help="The DPI of the output image")
parser.add_argument("--first", type=int, default=1, help="The first page to convert")
parser.add_argument("--last", type=int, default=None, help="The last page to convert")
args = parser.parse_args()


def main():
    # load config containing PDF_DIR and GYAZO_API_TOKEN
    # ~/.config/gyazo-pdf/config.yaml
    conf_path = Path(os.environ.get("HOME")) / ".config" / "gyazo-pdf" / "config.yaml"
    if not conf_path.exists():
        raise FileNotFoundError(f"Config file not found: {str(conf_path)}")
    with open(conf_path) as f:
        conf = yaml.safe_load(f)

    # PDF path
    pdf_dir = Path(conf["PDF_DIR"])
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

    # convert
    images = convert_from_path(
        pdf_path=path,
        dpi=args.dpi,
        first_page=args.first,
        last_page=args.last,
    )

    # upload to Gyazo
    client = Api(access_token=conf["GYAZO_API_TOKEN"])

    urls = []
    for image in tqdm(images, desc="Uploading..."):
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


if __name__ == "__main__":
    main()
