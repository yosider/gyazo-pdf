import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from math import ceil
from pathlib import Path

import click
import fitz
import pyperclip
import yaml
from gyazo import Api

from gyazo_pdf.processor import PageSuccess, max_workers, process_page


@click.command()
@click.argument("name", type=str, required=False, default="")
@click.option("--dpi", type=int, default=300, help="The DPI of the output image")
@click.option("--first", type=int, default=1, help="The first page to convert")
@click.option("--last", type=int, default=None, help="The last page to convert")
def main(
    name: str,
    dpi: int,
    first: int,
    last: int | None,
):
    """Convert PDF to images and upload to Gyazo.

    Before running this command, you need to set the following environment variables
    in `~/.config/gyazo-pdf/config.yaml`:
    ```
    GYAZO_API_TOKEN: your_gyazo_api_token
    PDF_DIR: /path/to/search/directory
    ```

    Args:
        name: The filename of the PDF to convert. If not specified, the latest PDF file in `PDF_DIR` will be used.
        dpi: The DPI of the output image.
        first: The first page to convert.
        last: The last page to convert. If not specified, all pages will be converted.
    """
    assert first > 0, "first must be greater than 0"
    assert last is None or last > first, "last must be greater than first"

    # load config
    conf_path = Path("~/.config/gyazo-pdf/config.yaml").expanduser()
    if not conf_path.exists():
        raise FileNotFoundError(f"Config file not found: {str(conf_path)}")
    with open(conf_path) as f:
        conf = yaml.safe_load(f)

    # gyazo client
    client = Api(access_token=conf["GYAZO_API_TOKEN"])

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

    # process pages
    with fitz.open(path) as doc:
        # 0-based page indices for `doc.pages(start, stop)`
        start_idx = first - 1
        stop_idx = doc.page_count if last is None else min(last, doc.page_count)  # convert all pages by default
        print(f"Processing from p.{first} to p.{stop_idx} / {doc.page_count}...")

        # Calculate zoom factor to adjust for desired DPI
        # PDF standard resolution is 72 DPI, so we divide the target DPI by 72
        zoom = dpi / 72
        # create a conversion matrix
        mat = fitz.Matrix(zoom, zoom)

        # process pages in parallel
        num_batches = ceil((stop_idx - start_idx) / max_workers)
        _process_page = partial(process_page, mat=mat, client=client, num_batches=num_batches, first=first)
        print(f"Number of workers: {max_workers}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(_process_page, doc.pages(start_idx, stop_idx))

    # extract urls and print errors
    urls = []
    for page_num, result in enumerate(results, start=first):
        if isinstance(result, PageSuccess):
            urls.append(result.url)
        else:  # PageFailure
            print("-" * 40)
            print(f"Error on Page {page_num}:")
            e = result.error
            traceback.print_exception(type(e), e, e.__traceback__)
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
