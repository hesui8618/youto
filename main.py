from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()
templates = Jinja2Templates(directory="templates")
executor = ThreadPoolExecutor(max_workers=2)

downloaded_videos = []

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return {
            'title': info.get('title'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'description': info.get('description'),
            'filesize': info.get('filesize'),
            'filepath': ydl.prepare_filename(info)
        }

def hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading {d['filename']}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "videos": downloaded_videos})

@app.post("/download", response_class=HTMLResponse)
async def download(request: Request, url: str = Form(...)):
    video_info = await executor.submit(download_video, url)
    downloaded_videos.append(video_info)
    return templates.TemplateResponse("index.html", {"request": request, "videos": downloaded_videos}) 