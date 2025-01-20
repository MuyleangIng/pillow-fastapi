from pathlib import Path
from html2image import Html2Image
from PIL import Image

def html_to_png(html_file, output_png, replacements=None):
    """
    Convert an HTML file to a PNG image without using a browser engine.

    :param html_file: Path to the HTML file.
    :param output_png: Path to save the output PNG file.
    :param replacements: Dictionary of placeholder-value pairs to replace in the HTML.
    """
    try:
        # Read the HTML file
        with open(html_file, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Replace placeholders with actual values
        if replacements:
            for placeholder, value in replacements.items():
                html_content = html_content.replace(placeholder, str(value))

        # Create a temporary file for the modified HTML
        temp_html = 'temp.html'
        with open(temp_html, 'w', encoding='utf-8') as file:
            file.write(html_content)

        # Configure html2image
        hti = Html2Image()

        # Convert HTML to PNG
        img_byte_arr = hti.screenshot(
            html_file=temp_html,
            save_as=output_png,
            size=(800, 600)  # Adjust size as needed
        )

        print(f"HTML successfully converted to PNG: {output_png}")

        # Optionally, you can further process the image using PIL
        # For example, to crop or resize
        with Image.open(output_png) as img:
            # Example: Crop the image
            # cropped_img = img.crop((0, 0, 500, 500))
            # cropped_img.save(output_png)
            pass

    except Exception as e:
        print(f"Error converting HTML to PNG: {e}")
    finally:
        # Clean up the temporary file
        Path(temp_html).unlink(missing_ok=True)

# Example usage
if __name__ == "__main__":
    # Path to the HTML file
    html_file = "index.html"

    # Path to save the output PNG file
    output_png = "output_card.png"

    # Replacements for placeholders in the HTML
    replacements = {
        "[Recipient Email]": "recipient@example.com",
        "[Sender Email]": "sender@example.com",
    }

    # Convert HTML to PNG
    html_to_png(html_file, output_png, replacements)