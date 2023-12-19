from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from database import Base, SessionLocal, engine
from sqlalchemy.orm import Session
import models
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app = FastAPI(title="to do app")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["health check"])
async def root():
 return {"message": "Hello World"}


@app.get("/index/", tags=["to do"], description="main entry point")
async def home(request: Request, db: Session = Depends(get_db)):
   todos = db.query(models.ToDo).all()
   return templates.TemplateResponse("base.html", {"request": request, "todos": todos})


@app.get("/index_no_html/", tags=["to do"], description="main entry point but without the html view. This is to view the DB only", deprecated=True)
async def home(db: Session = Depends(get_db)):
   todos = db.query(models.ToDo).all()
   return {"todos": todos}


@app.post("/add_no_html/", tags=["to do"], description="end point to add a todo but without the html view. This is to populate the DB only")
async def create_post(title: str = Form(...), db: Session = Depends(get_db)):
   new_todo = models.ToDo(title=title)
   db.add(new_todo)
   db.commit()
   db.refresh(new_todo)
   return new_todo


@app.post("/add/", tags=["to do"], description="end point to add a todo")
async def create_post(request: Request, title: str = Form(...), db: Session = Depends(get_db)):
   new_todo = models.ToDo(title=title)
   db.add(new_todo)
   db.commit()
#    db.refresh(new_todo)
   url = app.url_path_for("home")
   return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{todo_id}", tags=["to do"], description="update a task")
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
   todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
   print(f"looking for todo id: {todo_id}, todo :{todo}")
   todo.is_completed = not todo.is_completed
   db.commit()
#    db.refresh(todo)
   url = app.url_path_for("home")
   return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    db.delete(todo)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)