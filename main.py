from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import subprocess
import urllib.parse

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert(request: Request):
    webm_file = await request.form()
    webm_filename = webm_file['webmFile'].filename
    webm_path = f'uploads/{webm_filename}'

    mp4_filename = f'{os.path.splitext(webm_filename)[0]}.mp4'
    mp4_path = f'uploads/{mp4_filename}'

    with open(webm_path, 'wb') as buffer:
        shutil.copyfileobj(webm_file['webmFile'].file, buffer)

    # Conversion command using FFmpeg
    command = f'ffmpeg -i "{webm_path}" "{mp4_path}"'

    try:
        subprocess.run(command, shell=True, check=True)
        return templates.TemplateResponse("result.html", {"request": request, "mp4_filename": mp4_filename})
    except subprocess.CalledProcessError as e:
        return templates.TemplateResponse("result.html", {"request": request, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)