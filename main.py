from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import json

from converter import json_to_toon

app = FastAPI(title="JSON to TOON Converter", version="1.0.0")

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ConvertRequest(BaseModel):
    json_data: str


class ConvertResponse(BaseModel):
    toon: str


@app.post("/convert", response_model=ConvertResponse)
def convert(request: ConvertRequest):
    try:
        data = json.loads(request.json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    toon_output = json_to_toon(data)
    return ConvertResponse(toon=toon_output)


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = static_dir / "index.html"
    return HTMLResponse(content=html_path.read_text())
