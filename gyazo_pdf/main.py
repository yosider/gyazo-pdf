import os
from io import BytesIO
from pathlib import Path

import click
import fitz
import pyperclip
import yaml
from gyazo import Api
from PIL import Image
from tqdm import tqdm

doc = """
Convert PDF to images and upload to Gyazo.

NAME: The filename of the PDF to convert.
If not specified, the latest PDF file in PDF_DIR will be used.
"""


@click.command(help=doc)
@click.argument("name", type=str, default="")
@click.option("--dpi", type=int, default=300, help="The DPI of the output image")
@click.option("--first", type=int, default=1, help="The first page to convert")
@click.option("--last", type=int, default=None, help="The last page to convert")
def main(name, dpi, first, last):
    # load config containing PDF_DIR and GYAZO_API_TOKEN
    # ~/.config/gyazo-pdf/config.yaml
    conf_path = Path(os.environ.get("HOME")) / ".config" / "gyazo-pdf" / "config.yaml"
    if not conf_path.exists():
        raise FileNotFoundError(f"Config file not found: {str(conf_path)}")
    with open(conf_path) as f:
        conf = yaml.safe_load(f)

    # PDF path
    pdf_dir = Path(conf["PDF_DIR"])
    if name != "":
        path = pdf_dir / f"{name}.pdf"
    else:
        # If no name is specified, get the latest pdf file in PDF_DIR
        print("Getting the latest PDF file")
        pdfs = list(pdf_dir.glob("*.pdf"))
        if len(pdfs) == 0:
            raise FileNotFoundError(f"No PDF files found in {str(pdf_dir)}.")
        path = max(pdfs, key=os.path.getctime)

    print(f"Loading {path.name}...")
    doc = fitz.open(path)

    if last is not None:
        last_page_str = f"p.{last}"
    else:
        last = doc.page_count
        last_page_str = f"p.{last} (the last page)"
    print(f"Converting from p.{first} to {last_page_str}...")

    # Calculate zoom factor to adjust for desired DPI
    # PDF standard resolution is 72 DPI, so we divide the target DPI by 72
    zoom = dpi / 72
    # create a conversion matrix
    mat = fitz.Matrix(zoom, zoom)

    images = []
    for page_num in range(first - 1, last):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

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

    # copy to clipboard with the following format
    # [https://gyazo.com/image_id_1]
    # [https://gyazo.com/image_id_2]
    # ...
    # [https://gyazo.com/image_id_N]
    # This format is intended for pasting into Cosense
    pyperclip.copy("[" + "]\n[".join(urls) + "]\n")


if __name__ == "__main__":
    main()
