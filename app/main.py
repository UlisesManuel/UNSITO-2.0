# ==============================================================================
# 1. TODAS LAS IMPORTACIONES (HASTA ARRIBA)
# ==============================================================================
import os
import shutil
from fastapi import FastAPI, Depends, Request, HTTPException, Form, Response, Cookie, File, UploadFile
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

# Configurar directorio para almacenar las imágenes subidas físicamente
IMAGENES_DIR = os.path.join(BASE_DIR, "static", "imagenes")
os.makedirs(IMAGENES_DIR, exist_ok=True)

# Configurar el motor de plantillas Jinja2
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Simulación de credenciales fijas para el Administrador
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def es_administrador(request: Request):
    """Función auxiliar para verificar si el usuario está logueado mediante cookies"""
    return request.cookies.get("sesion_admin") == "activa"

def verificar_admin_cookie(request: Request):
    """
    Dependencia de seguridad que valida la cookie del administrador.
    Si no es válida, interrumpe la petición lanzando una redirección limpia.
    """
    if request.cookies.get("sesion_admin") != "activa":
        raise HTTPException(
            status_code=303, 
            headers={"Location": "/login"},
            detail="No autorizado"
        )
    return True

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
# 4. RUTAS DE ADMINISTRACIÓN (PANEL PRIVADO BLINDADO Y CON SOPORTE PARA ARCHIVOS)
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
def admin_dashboard(request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    noticias = crud.obtener_todas_las_noticias_admin(db)
    return templates.TemplateResponse(request, "admin/dashboard.html", {"noticias": noticias})

@app.get("/admin/crear")
def formulario_crear_noticia(request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    secciones = db.query(models.Seccion).all()
    return templates.TemplateResponse(request, "admin/crear.html", {"secciones": secciones})

@app.post("/admin/crear")
def guardar_nueva_noticia(
    titulo: str = Form(...), 
    contenido: str = Form(...),
    seccion_id: int = Form(...), 
    imagen: UploadFile = File(...), # Recibe el archivo binario real
    db: Session = Depends(get_db), 
    _=Depends(verificar_admin_cookie)
):
    # Guardar el archivo físicamente en el servidor
    ruta_archivo_local = os.path.join(IMAGENES_DIR, imagen.filename)
    with open(ruta_archivo_local, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)
        
    # Ruta web que se guardará en la base de datos
    imagen_url = f"/static/imagenes/{imagen.filename}"
    
    crud.crear_noticia(db=db, titulo=titulo, contenido=contenido, imagen_url=imagen_url, seccion_id=seccion_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/editar/{noticia_id}")
def formulario_editar_noticia(noticia_id: int, request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    secciones = db.query(models.Seccion).all()
    return templates.TemplateResponse(request, "admin/editar.html", {"noticia": noticia, "secciones": secciones})

@app.post("/admin/editar/{noticia_id}")
def actualizar_noticia(
    noticia_id: int, 
    titulo: str = Form(...), 
    contenido: str = Form(...),
    seccion_id: int = Form(...), 
    imagen: UploadFile = File(None), # El archivo es opcional al editar
    db: Session = Depends(get_db), 
    _=Depends(verificar_admin_cookie)
):
    imagen_url = None
    # Si el usuario subió una nueva imagen, la guardamos; de lo contrario, el CRUD mantiene la ruta vieja
    if imagen and imagen.filename:
        ruta_archivo_local = os.path.join(IMAGENES_DIR, imagen.filename)
        with open(ruta_archivo_local, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        imagen_url = f"/static/imagenes/{imagen.filename}"

    crud.modificar_noticia(db=db, noticia_id=noticia_id, titulo=titulo, contenido=contenido, imagen_url=imagen_url, seccion_id=seccion_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/eliminar/{noticia_id}")
def borrar_noticia_ruta(noticia_id: int, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    crud.eliminar_noticia(db=db, noticia_id=noticia_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)