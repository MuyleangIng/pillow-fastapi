# Christmas Card Generator

This project is a FastAPI application that generates personalized Christmas cards by adding email addresses to a template image.

## Requirements

Make sure you have Python 3.7+ installed on your system. The required packages are listed in `requirements.txt`.

## Installation

1. **Set up a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI server:**

   ```bash
   uvicorn main:app --reload
   ```

   The server will start running at `http://localhost:8000`.

## Testing the API

You can test the API using `curl`, Postman, or any HTTP client. Here's an example using `curl`:

```bash
curl -X POST http://localhost:8000/create-christmas-card/ \
  -H "Content-Type: application/json" \
  -d '{
      "to_email": "muyleanging@gmail.com",
      "from_email": "test@gmail.com",
      "font_size": 40,
      "color": "navy"
  }'
```

## API Endpoint

### Create Christmas Card

- **URL:** `/create-christmas-card/`
- **Method:** `POST`
- **Request Body:**

  ```json
  {
    "to_email": "recipient@example.com",
    "from_email": "sender@example.com",
    "font_size": 40,
    "color": "navy"
  }
  ```

- **Response:**

  - **Success:** Returns the generated Christmas card image.
  - **Error:** Returns an error message with a status code.

## Example Response

```json
{
  "message": "Christmas card generated successfully!",
  "image_url": "http://localhost:8000/generated_cards/christmas_card_12345.png"
}
```

## Notes

- Ensure that the `generated_cards` directory exists and is writable by the application.
- You can customize the template image and font settings in the code.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to modify the content as per your project's specific requirements!