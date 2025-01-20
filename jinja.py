from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from html2image import Html2Image
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class CardData(BaseModel):
    title: str
    recipient_email: str
    sender_email: str
    message: str

@app.post("/generate-png")
async def generate_png(card_data: CardData):
    try:
        # Render the template with the provided data
        html_content = templates.get_template("card_template.html").render(card_data.dict())

        # Write the rendered HTML to a temporary file
        temp_html_path = "temp.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert HTML to PNG
        hti = Html2Image()
        output_png = "output_card.png"
        hti.screenshot(
            html_file=temp_html_path,
            save_as=output_png,
            size=(800, 600)  # Adjust size as needed
        )

        # Clean up the temporary HTML file
        os.remove(temp_html_path)

        # Return the PNG file
        return FileResponse(output_png, media_type="image/png", filename="card.png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)