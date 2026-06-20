from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from .database import engine, Base, get_db
from . import models

# Crear las tablas en la base de datos automáticamente al arrancar
Base.metadata.create_base_all(bind=engine)

app = FastAPI(title="EL UNSITO 2.0")

# Obtener la ruta absoluta del directorio "app" para evitar fallos con Jinja2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos (CSS, JS, Imágenes)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar el motor de plantillas Jinja2
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    """
    Ruta principal del portal.
    Aquí enviaremos las noticias del carrusel y las más recientes.
    """
    # Por ahora solo renderiza el index.html sin datos reales
    return templates.TemplateResponse("index.html", {"request": request})