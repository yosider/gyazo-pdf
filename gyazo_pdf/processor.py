import os
from dataclasses import dataclass
from io import BytesIO

import fitz
from gyazo import Api
from PIL import Image

max_workers = min(32, (os.cpu_count() or 1) + 4)


@dataclass
class PageSuccess:
    """Successful page processing result."""

    url: str


@dataclass
class PageFailure:
    """Failed page processing result."""

    error: Exception


PageResult = PageSuccess | PageFailure


def process_page(
    page: fitz.Page,
    mat: fitz.Matrix,
    client: Api,
    num_batches: int,
    first: int,
) -> PageResult:
    """Convert a page to an image and upload to Gyazo."""
    try:
        idx_batch, idx_in_batch = divmod(page.number - first, max_workers)

        # convert to image
        if idx_in_batch == 0:
            print(f"Batch {idx_batch + 1} / {num_batches}: Converting to image...")
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # save the image to a byte array because client.upload_image expects image data in BinaryIO
        with BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)

            # upload
            if idx_in_batch == 0:
                print(f"Batch {idx_batch + 1} / {num_batches}: Uploading to Gyazo...")
            res = client.upload_image(img_byte_arr)

        url = res.url
        if url is None:
            raise ValueError("Upload succeeded but URL is None")
        url = url.replace("i.gyazo.com", "gyazo.com").replace(".png", "")

        return PageSuccess(url=url)
    except Exception as e:
        return PageFailure(error=e)
