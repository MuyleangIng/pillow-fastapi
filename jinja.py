from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from html2image import Html2Image
import os
import uuid
from datetime import datetime, timedelta
import glob
import asyncio
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount the generated_cards directory as a static directory
app.mount("/images", StaticFiles(directory="generated_cards"), name="images")

class CardData(BaseModel):
    title: str
    recipient_email: str
    sender_email: str
    message: str

class ImageResponse(BaseModel):
    image_id: str
    view_url: str
    download_url: str
    expires_at: datetime

# Configuration
OUTPUT_DIR = "generated_cards"
MAX_IMAGE_AGE_HOURS = 1
BASE_URL = "http://localhost:8000"  # Change this to your actual domain

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def cleanup_old_files():
    """Remove files older than MAX_IMAGE_AGE_HOURS"""
    while True:
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=MAX_IMAGE_AGE_HOURS)
            
            for file_path in glob.glob(f"{OUTPUT_DIR}/*.png"):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_creation_time < cutoff_time:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")
            
            await asyncio.sleep(1800)
        except Exception as e:
            print(f"Error in cleanup task: {e}")
            await asyncio.sleep(1800)

@app.on_event("startup")
async def startup_event():
    """Start the cleanup task when the application starts"""
    asyncio.create_task(cleanup_old_files())

def cleanup_file(file_path: str):
    """Remove a specific file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error removing file {file_path}: {e}")

@app.post("/generate-png", response_model=ImageResponse)
async def generate_png(card_data: CardData, background_tasks: BackgroundTasks):
    try:
        # Generate unique filename using UUID
        unique_id = str(uuid.uuid4())
        temp_html_path = os.path.join(OUTPUT_DIR, f"temp_{unique_id}.html")
        output_png = os.path.join(OUTPUT_DIR, f"card_{unique_id}.png")
        filename = f"card_{unique_id}.png"

        # Render the template with the provided data
        html_content = templates.get_template("card_template.html").render(card_data.dict())

        # Write the rendered HTML to a temporary file
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert HTML to PNG
        hti = Html2Image(output_path=OUTPUT_DIR)
        hti.screenshot(
            html_file=temp_html_path,
            save_as=filename,
            size=(800, 600)
        )

        # Clean up the temporary HTML file
        try:
            os.remove(temp_html_path)
        except Exception as e:
            print(f"Error removing temporary HTML file: {e}")

        # Schedule the PNG file for deletion after MAX_IMAGE_AGE_HOURS
        background_tasks.add_task(cleanup_file, output_png)

        # Calculate expiration time
        expires_at = datetime.now() + timedelta(hours=MAX_IMAGE_AGE_HOURS)

        # Return URLs and metadata
        return ImageResponse(
            image_id=unique_id,
            view_url=f"{BASE_URL}/view/{unique_id}",
            download_url=f"{BASE_URL}/images/{filename}",
            expires_at=expires_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/view/{image_id}")
async def view_image(image_id: str):
    """View the image in HTML page"""
    filename = f"card_{image_id}.png"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Return a simple HTML page displaying the image
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>View Generated Card</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
            }}
            .image-container {{
                max-width: 800px;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
            .download-link {{
                display: block;
                text-align: center;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="image-container">
            <img src="/images/{filename}" alt="Generated Card">
            <a href="/images/{filename}" download class="download-link">Download Image</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)