from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from shared.memory import stats_data, stats_lock
from backend.database import get_weekly_usage, get_monthly_usage
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "frontend" / "dist"   

app = FastAPI()
app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_with_threshold(raw_data_dict, threshold=30): #default 30s
    filtered = {}
    others_time = 0
    
    for app, duration in raw_data_dict.items():
        if duration < threshold:
            others_time += duration
        else:
            filtered[app] = round(duration, 1)
            
    if others_time > 0:
        filtered["Others"] = round(others_time, 1)
        
    return dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True))

@app.get("/daily")
def get_stats():
    with stats_lock:
        data = stats_data.copy()
    return format_with_threshold(data, threshold=20)

@app.get("/api/weekly")
def weekly_stats():
    raw_weekly = get_weekly_usage()

    today = datetime.today()
    last_7_days = [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(6, -1, -1)
    ]

    result = {}

    for day in last_7_days:
        apps = raw_weekly.get(day, {})
        result[day] = format_with_threshold(apps, threshold=60)

    return result

@app.get("/api/monthly")
def monthly_stats():
    raw_monthly = get_monthly_usage()
    return {day: format_with_threshold(apps, threshold=300) for day, apps in raw_monthly.items()}

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    file_path = DIST_DIR / full_path
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    return FileResponse(DIST_DIR / "index.html")


def run_api():
    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
