import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

import click
import fitz
import pyperclip
import yaml
from gyazo import Api
from PIL import Image


def process_page(
    page: fitz.Page,
    mat: fitz.Matrix,
    client: Api,
) -> tuple[str | None, Exception | None]:
    """Convert a page to an image and upload to Gyazo."""
    try:
        # convert to image
        if page.number == 0:
            print("Converting to image...")
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # save the image to a byte array because client.upload_image expects image data in bytes
        with BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format="PNG")
            img_byte_data = img_byte_arr.getvalue()

        # upload
        if page.number == 0:
            print("Uploading to Gyazo...")
        res = client.upload_image(img_byte_data)
        url = res.url.replace("i.gyazo.com", "gyazo.com").replace(".png", "")

        return url, None
    except Exception as e:
        return None, e


@click.command()
@click.argument("name", type=str, required=False, default="")
@click.option("--dpi", type=int, default=300, help="The DPI of the output image")
@click.option("--first", type=int, default=1, help="The first page to convert")
@click.option("--last", type=int, default=None, help="The last page to convert")
def main(
    name: str,
    dpi: int,
    first: int,
    last: int,
):
    """Convert PDF to images and upload to Gyazo.

    NAME: The filename of the PDF to convert. If not specified, the latest PDF file in PDF_DIR will be used.

    \b
    Before running this command, you need to set the following environment variables
    in ~/.config/gyazo-pdf/config.yaml:
    ```
    GYAZO_API_TOKEN: your_gyazo_api_token
    PDF_DIR: /Path/to/pdf/directory
    ```
    """
    # load config
    conf_path = Path(os.environ.get("HOME")) / ".config" / "gyazo-pdf" / "config.yaml"
    if not conf_path.exists():
        raise FileNotFoundError(f"Config file not found: {str(conf_path)}")
    with open(conf_path) as f:
        conf = yaml.safe_load(f)

    # get the PDF path
    pdf_dir = Path(conf["PDF_DIR"])
    if name != "":
        path = pdf_dir / f"{name}.pdf"
    else:
        # If no name is specified, get the latest pdf in PDF_DIR
        print("Getting the latest PDF...")
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
    print(f"Processing from p.{first} to {last_page_str}...")

    # Calculate zoom factor to adjust for desired DPI
    # PDF standard resolution is 72 DPI, so we divide the target DPI by 72
    zoom = dpi / 72
    # create a conversion matrix
    mat = fitz.Matrix(zoom, zoom)

    # gyazo client
    client = Api(access_token=conf["GYAZO_API_TOKEN"])

    # process pages in parallel
    def _process_page(page):
        return process_page(page, mat, client)

    with ThreadPoolExecutor() as executor:
        results = executor.map(_process_page, doc.pages(first - 1, last))

    # extract urls and errors
    urls = []
    failed_pages = []
    for page_num, (url, error) in enumerate(results, start=first):
        if url is not None:
            urls.append(url)
        else:
            failed_pages.append((page_num, error))

    # print errors
    if failed_pages:
        print("Failed to process the following pages:")
        for page_num, error in failed_pages:
            print("-" * 40)  # separator
            print(f"Error on Page {page_num}:")
            traceback.print_exception(type(error), error, error.__traceback__)
        print("-" * 40)

    # copy urls to clipboard with the following format
    # [https://gyazo.com/image_id_1]
    # [https://gyazo.com/image_id_2]
    # ...
    # [https://gyazo.com/image_id_N]
    # This format is intended for pasting into Cosense
    pyperclip.copy("[" + "]\n[".join(urls) + "]\n")

    print(f"Successfully converted and uploaded {len(urls)} pages.")
    print("URLs have been copied to clipboard.")


if __name__ == "__main__":
    main()
