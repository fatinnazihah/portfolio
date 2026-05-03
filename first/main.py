import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Project

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# DATABASE CONFIGURATION
# Pulls from Render Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for Render/SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Default to SQLite for local testing if no DB URL is found
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"projects": projects}
    )

@app.post("/add-project")
def add_project(
    title: str = Form(...),
    description: str = Form(...),
    image_url: str = Form(None),
    video_url: str = Form(None),
    tech_stack: str = Form(None),
    db: Session = Depends(get_db)
):
    # Logic to convert standard YT links to Embed links
    if video_url and "watch?v=" in video_url:
        video_url = video_url.replace("watch?v=", "embed/")
    
    new_project = Project(
        title=title, 
        description=description, 
        image_url=image_url, 
        video_url=video_url,
        tech_stack=tech_stack
    )
    db.add(new_project)
    db.commit()
    return RedirectResponse(url="/", status_code=303)