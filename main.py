import os
import shutil
import subprocess
import sys
import argparse
import uvicorn
from typing import Optional

from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

SUPPORTED_FORMATS = ["mp4", "mkv", "avi", "mp3", "wav"]

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert_web(
    request: Request,
    media_file: UploadFile = Form(...),
    output_format: str = Form(...)
):
    try:
        converted_filename = convert_file(media_file.file, media_file.filename, output_format)
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "converted_filename": converted_filename},
        )
    except (subprocess.CalledProcessError, ValueError, ValidationError) as e:
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": str(e)},
        )

def convert_file(file, filename, output_format):
    if output_format.lower() not in SUPPORTED_FORMATS:
        raise ValueError("Invalid output format.")

    media_filename = filename
    media_path = f"uploads/{media_filename}"
    with open(media_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    converted_filename = f"{os.path.splitext(media_filename)[0]}.{output_format}"
    converted_path = f"uploads/{converted_filename}"
    command = f'ffmpeg -i "{media_path}" "{converted_path}"'

    subprocess.run(command, shell=True, check=True)

    return converted_filename

def convert_cli(input_file: str, output_format: str, output_file: Optional[str] = None):
    if output_file is None:
        output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
    
    # Extract the filename from the full file path
    input_filename = os.path.basename(input_file)

    with open(input_file, "rb") as file:
        convert_file(file, input_filename, output_format)

    print(f"Conversion complete! The file is ready: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Converter CLI")
    parser.add_argument("-i", "--input_file", help="Path to the input media file")
    parser.add_argument("-o", "--output_format", help="Output format for conversion")
    parser.add_argument("-of", "--output_file", help="Path to the output file (optional)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No command-line arguments provided, start the web server
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Command-line arguments provided, perform conversion
        convert_cli(args.input_file, args.output_format, args.output_file)