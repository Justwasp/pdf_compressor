import streamlit as st
from io import BytesIO
import fitz
from PIL import Image
from typing import Optional
import time


def compress_pdf_bytes(
    pdf_bytes: bytes,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    image_quality: int = 70,
    dpi: int = 120,
    new_width: int = 800,
    preserve_color: bool = False,
    status_placeholder=None,
) -> bytes:
    """Compress a PDF represented by bytes.

    If preserve_color is False the pages are converted to grayscale (existing behavior).
    If preserve_color is True pages will be kept in RGB color.
    """
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(pdf_document)

    page_range_start = max(1, start_page or 1)
    page_range_end = min(total_pages, end_page or total_pages)

    images = []

    num_pages_to_process = page_range_end - page_range_start + 1
    loop_start_time = time.time()

    for i in range(page_range_start - 1, page_range_end):
        page_progress = i - (page_range_start - 1) + 1
        if status_placeholder:
            elapsed_time = time.time() - loop_start_time
            status_placeholder.text(
                f"Compressing page {page_progress}/{num_pages_to_process}... "
                f"({elapsed_time:.2f}s elapsed)"
            )

        page = pdf_document[i]
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(BytesIO(pix.tobytes("png")))
        w, h = img.size
        new_h = int(h * new_width / w)
        # preserve color when requested, otherwise keep existing grayscale conversion
        if preserve_color:
            img = img.resize((new_width, new_h), Image.Resampling.LANCZOS).convert("RGB")
        else:
            img = img.resize((new_width, new_h), Image.Resampling.LANCZOS).convert("L")
        images.append(img)

    if not images:
        raise ValueError("No pages selected to compress")

    if status_placeholder:
        elapsed_time = time.time() - loop_start_time
        status_placeholder.text(f"Finalizing PDF... ({elapsed_time:.2f}s elapsed)")

    output = BytesIO()
    # If images are color (RGB), Pillow will embed color images into the PDF;
    # quality still controls JPEG compression used inside PDF when saving.
    images[0].save(
        output,
        format="PDF",
        save_all=True,
        append_images=images[1:],
        quality=image_quality,
    )
    output.seek(0)
    return output.read()


def image_bytes_to_pdf_bytes(image_bytes: bytes) -> bytes:
    """Convert image bytes (JPEG/PNG) to a single-page PDF (in-memory).

    Ensures the image is RGB (no alpha) before saving to PDF.
    """
    img = Image.open(BytesIO(image_bytes))
    # Convert any non-RGB mode (including RGBA/LA/P) to RGB for PDF
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    # For consistency, convert grayscale images to RGB too (PIL will handle)
    output = BytesIO()
    img.save(output, format="PDF")
    output.seek(0)
    return output.read()


# ------------- Streamlit UI ----------------


def main():
    st.title("PDF / Image Compressor")

    # accept pdf and common image types
    uploaded_file = st.file_uploader(
        "Upload a PDF or image", type=["pdf", "jpg", "jpeg", "png"]
    )

    col1, col2 = st.columns(2)
    with col1:
        image_quality = st.number_input("Image quality (JPEG)", min_value=10, max_value=100, value=70)
        dpi = st.number_input("DPI (rendering resolution)", min_value=72, max_value=300, value=120)
    with col2:
        new_width = st.number_input("Page width (pixels)", min_value=400, max_value=1600, value=800)

    # New: choose grayscale or color
    color_mode = st.radio("Color mode", ("Grayscale", "Color"), index=0)
    preserve_color = color_mode == "Color"

    start_page = st.number_input(
        "Start page (leave 0 for first)", min_value=0, value=0
    )
    end_page = st.number_input("End page (0 = last page)", min_value=0, value=0)

    if uploaded_file is not None:
        st.write(f"File: **{uploaded_file.name}**")
        raw_bytes = uploaded_file.read()
        content_type = (uploaded_file.type or "").lower()

        # If an image was uploaded, show preview and convert to PDF bytes
        is_image = content_type.startswith(
            "image/"
        ) or uploaded_file.name.lower().endswith((".jpg", ".jpeg", ".png"))

        if is_image:
            try:
                st.image(raw_bytes, caption="Preview", use_column_width=True)
                pdf_bytes = image_bytes_to_pdf_bytes(raw_bytes)
                base_name = uploaded_file.name.rsplit(".", 1)[0]
            except Exception as e:
                st.error(f"Failed to convert image to PDF: {e}")
                pdf_bytes = None
                base_name = uploaded_file.name.rsplit(".", 1)[0]
        else:
            # assume PDF
            pdf_bytes = raw_bytes
            base_name = uploaded_file.name.rsplit(".", 1)[0]

        if pdf_bytes and st.button("Compress PDF"):
            status_placeholder = st.empty()
            status_placeholder.text("Starting compression...")

            start_time = time.time()
            compressed_bytes = None

            try:
                compressed_bytes = compress_pdf_bytes(
                    pdf_bytes=pdf_bytes,
                    start_page=None if start_page == 0 else start_page,
                    end_page=None if end_page == 0 else end_page,
                    image_quality=image_quality,
                    dpi=dpi,
                    new_width=new_width,
                    preserve_color=preserve_color,
                    status_placeholder=status_placeholder,
                )
            except Exception as e:
                status_placeholder.error(f"Compression failed: {e}")

            if compressed_bytes:
                end_time = time.time()
                elapsed_time = end_time - start_time
                status_placeholder.success(f"Done in {elapsed_time:.2f} seconds!")
                out_name = f"{base_name}_compressed.pdf"
                st.download_button(
                    label="Download compressed PDF",
                    data=compressed_bytes,
                    file_name=out_name,
                    mime="application/pdf",
                )

    st.markdown("### ☕ Support")
    st.markdown(
        """
        If this app helped you and you'd like to say thanks,  
        you can [buy me a coffee](https://buymeacoffee.com/justwasp) ☕
        """
    )

if __name__ == "__main__":
    main()
