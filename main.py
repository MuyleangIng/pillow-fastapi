from fastapi import FastAPI, HTTPException
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import JSONResponse
from io import BytesIO
import requests
from pydantic import BaseModel
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

SAVE_DIR = "D:/pillow"
os.makedirs(SAVE_DIR, exist_ok=True)

class ChristmasCard(BaseModel):
    to_email: str
    from_email: str
    font_size: int = 30
    color: str = "navy"

@app.post("/create-christmas-card/")
async def create_christmas_card(card_data: ChristmasCard):
    try:
        # Download the Christmas card template
        response = requests.get("https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Blue%20Illustrated%20Christmas%20Label.jpg-aJ5WgDjHxGyZEIXGEVW5IgWLPVj7X9.jpeg")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download template")
        
        # Open image
        image = Image.open(BytesIO(response.content))
        draw = ImageDraw.Draw(image)
        
        # Try to load a font that works well with emails
        try:
            font = ImageFont.truetype("arial.ttf", card_data.font_size)
        except:
            font = ImageFont.load_default()

        # Corrected positions for proper alignment with the lines
        to_position = (400, 585)    # Adjusted "To" position
        from_position = (400, 805)  # Adjusted "From" position

        # Draw the emails with corrected positions
        draw.text(to_position, card_data.to_email, font=font, fill=card_data.color)
        draw.text(from_position, card_data.from_email, font=font, fill=card_data.color)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"christmas_card_{timestamp}.png"
        file_path = os.path.join(SAVE_DIR, filename)

        # Save the image
        image.save(file_path)
        logger.info(f"Christmas card saved to: {file_path}")

        return JSONResponse(
            status_code=200,
            content={
                "message": "Christmas card created successfully",
                "saved_location": file_path,
                "filename": filename,
                "to_email": card_data.to_email,
                "from_email": card_data.from_email
            }
        )

    except Exception as e:
        logger.error(f"Error creating Christmas card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))