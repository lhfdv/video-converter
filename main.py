import os
import shutil
import subprocess
import urllib.parse

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
async def convert(
    request: Request,
    media_file: UploadFile = Form(...),
    output_format: str = Form(...)
):
    try:
        if output_format.lower() not in SUPPORTED_FORMATS:
            raise ValueError("Invalid output format.")

        media_filename = media_file.filename
        media_path = f"uploads/{media_filename}"
        with open(media_path, "wb") as buffer:
            shutil.copyfileobj(media_file.file, buffer)

        converted_filename = f"{os.path.splitext(media_filename)[0]}.{output_format}"
        converted_path = f"uploads/{converted_filename}"
        command = f'ffmpeg -i "{media_path}" "{converted_path}"'

        subprocess.run(command, shell=True, check=True)

        return templates.TemplateResponse(
            "result.html",
            {"request": request, "converted_filename": converted_filename},
        )
    except (subprocess.CalledProcessError, ValueError, ValidationError) as e:
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": str(e)},
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)