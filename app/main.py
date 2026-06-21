# ==============================================================================
# 1. TODAS LAS IMPORTACIONES (HASTA ARRIBA)
# ==============================================================================
import os
from fastapi import FastAPI, Depends, Request, HTTPException, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, crud

# ==============================================================================
# 2. CONFIGURACIÓN E INICIALIZACIÓN DE LA APP
# ==============================================================================
# Inicializar las tablas en la base de datos automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EL UNSITO 2.0")

# Configurar rutas absolutas para directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos (CSS, JS, Imágenes)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar el motor de plantillas Jinja2
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Simulación de credenciales fijas para el Administrador
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def es_administrador(request: Request):
    """Función auxiliar para verificar si el usuario está logueado mediante cookies"""
    return request.cookies.get("sesion_admin") == "activa"

# ==============================================================================
# 3. RUTAS PÚBLICAS
# ==============================================================================

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    noticias_carrusel = crud.obtener_noticias_carrusel(db, limite_por_seccion=2)
    noticias_recientes = crud.obtener_noticias_recientes(db, limite=6)
    return templates.TemplateResponse(
        request,
        "index.html", 
        {"carrusel": noticias_carrusel, "recientes": noticias_recientes}
    )

@app.get("/seccion/{slug}")
def ver_seccion(slug: str, request: Request, db: Session = Depends(get_db)):
    seccion = db.query(models.Seccion).filter(models.Seccion.slug == slug).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    noticias = crud.obtener_noticias_por_seccion(db, seccion_slug=slug)
    return templates.TemplateResponse(
        request,
        "seccion.html", 
        {"seccion": seccion, "noticias": noticias}
    )

@app.get("/noticia/{noticia_id}")
def ver_noticia(noticia_id: int, request: Request, db: Session = Depends(get_db)):
    noticia = crud.obtener_noticia_y_contar_visita(db, noticia_id=noticia_id)
    if not noticia:
        raise HTTPException(status_code=404, detail="La noticia no existe")
    return templates.TemplateResponse(
        request,
        "noticia.html", 
        {"noticia": noticia}
    )

# ==============================================================================
# 4. RUTAS DE ADMINISTRACIÓN (PANEL PRIVADO CORREGIDO)
# ==============================================================================

@app.get("/login")
def mostrar_login(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.post("/login")
def procesar_login(response: Response, usuario: str = Form(...), password: str = Form(...)):
    if usuario == ADMIN_USER and password == ADMIN_PASS:
        respuesta = RedirectResponse(url="/admin/dashboard", status_code=303)
        respuesta.set_cookie(key="sesion_admin", value="activa", httponly=True)
        return respuesta
    return RedirectResponse(url="/login?error=true", status_code=303)

@app.get("/logout")
def cerrar_sesion():
    respuesta = RedirectResponse(url="/", status_code=303)
    respuesta.delete_cookie("sesion_admin")
    return respuesta

@app.get("/admin/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not es_administrador(request):
        return RedirectResponse(url="/login", status_code=303)
    noticias = crud.obtener_todas_las_noticias_admin(db)
    return templates.TemplateResponse(request, "admin/dashboard.html", {"noticias": noticias})

@app.get("/admin/crear")
def formulario_crear_noticia(request: Request, db: Session = Depends(get_db)):
    if not es_administrador(request):
        return RedirectResponse(url="/login", status_code=303)
    secciones = db.query(models.Seccion).all()
    return