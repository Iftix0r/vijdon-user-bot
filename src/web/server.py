from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.models import get_db, SourceGroup, Log
from sqlalchemy.orm import Session
import os

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.timestamp.desc()).limit(50).all()
    groups = db.query(SourceGroup).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "logs": logs,
        "groups": groups,
        "passenger_count": db.query(Log).filter(Log.is_passenger == True).count(),
        "total_messages": db.query(Log).count()
    })
