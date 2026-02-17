from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.models import get_db, SourceGroup, Log, Blacklist
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.timestamp.desc()).limit(10).all()
    groups = db.query(SourceGroup).all()
    blacklist = db.query(Blacklist).all()
    
    # Stats for charts
    passenger_count = db.query(Log).filter(Log.is_passenger == True).count()
    driver_count = db.query(Log).filter(Log.is_passenger == False).count()
    
    # Hourly stats (last 24 hours)
    # This is a bit complex for SQLite but we can do a simple version
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "logs": logs,
        "groups": groups,
        "blacklist": blacklist,
        "passenger_count": passenger_count,
        "driver_count": driver_count,
        "total_messages": db.query(Log).count(),
        "active_groups": db.query(SourceGroup).filter(SourceGroup.active == True).count()
    })

@app.post("/blacklist")
async def add_to_blacklist(user_id: str, reason: str = None, db: Session = Depends(get_db)):
    item = Blacklist(user_id=user_id, reason=reason)
    db.add(item)
    db.commit()
    return {"status": "ok"}
