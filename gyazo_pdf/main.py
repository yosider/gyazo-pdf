import os
from io import BytesIO
from pathlib import Path

import click
import pyperclip
import yaml
from gyazo import Api
from pdf2image import convert_from_path
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
        # get the latest pdf file in PDF_DIR
        pdfs = list(pdf_dir.glob("*.pdf"))
        if len(pdfs) == 0:
            raise FileNotFoundError(f"No PDF files found in {str(pdf_dir)}.")
        path = max(pdfs, key=os.path.getctime)
        print(f"Latest PDF file: {path.name}")

    last_page_str = "the last page" if last is None else f"p.{last}"
    print(f"Converting from p.{first} to {last_page_str}...")

    # convert
    images = convert_from_path(
        pdf_path=path,
        dpi=dpi,
        first_page=first,
        last_page=last,
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
