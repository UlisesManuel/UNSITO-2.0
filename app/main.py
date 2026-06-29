# TODAS LAS IMPORTACIONES
import os
import shutil
from fastapi import FastAPI, Depends, Request, HTTPException, Form, Response, Cookie, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, crud

# 2. CONFIGURACIÓN E INICIALIZACIÓN DE LA APP

# Inicializar las tablas en la base de datos automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EL UNSITO 2.0")

# Configurar rutas absolutas para directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos 
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar directorio para almacenar las imágenes subidas físicamente
IMAGENES_DIR = os.path.join(BASE_DIR, "static", "imagenes")
os.makedirs(IMAGENES_DIR, exist_ok=True)

# Configurar el motor de plantillas Jinja2
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Simulación de credenciales fijas para el Administrador
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

#Revisa si existe una cookie
def es_administrador(request: Request):
    """Función para verificar si el usuario está logueado mediante cookies"""
    #Si encuentra una retorna true si no false;
    return request.cookies.get("sesion_admin") == "activa"

def verificar_admin_cookie(request: Request):
    """
    Dependencia que valida la cookie del administrador.
    Si no es válida, interrumpe la petición lanzando una redirección limpia.
    """
    if request.cookies.get("sesion_admin") != "activa":
        raise HTTPException(
            status_code=303, 
            headers={"Location": "/login"},
            detail="No autorizado"
        )
    return True


# 3. RUTAS PÚBLICAS
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    noticias_carrusel = crud.obtener_noticias_carrusel(db, limite_por_seccion=2 )
    noticias_recientes = crud.obtener_noticias_recientes(db, limite=6)
    return templates.TemplateResponse(
        request,
        "index.html", 
        {"carrusel": noticias_carrusel, "recientes": noticias_recientes}
    )
#Ruta de las secciones
@app.get("/seccion/{slug}")
def ver_seccion(slug: str, request: Request, db: Session = Depends(get_db)):
    #Filtra por secciones
    seccion = db.query(models.Seccion).filter(
        (models.Seccion.slug == slug.lower()) | 
        (models.Seccion.nombre.ilike(slug))
    ).first()
    #Regresa un error si no la encuentra
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
        
    noticias = crud.obtener_noticias_por_seccion(db, seccion_slug=seccion.slug)
    return templates.TemplateResponse(
        request,
        "seccion.html", 
        {"seccion": seccion, "noticias": noticias}
    )
#Ver noticias
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

# 4. RUTAS DE ADMINISTRACIÓN 
#Ruta que muestra login
@app.get("/login")
def mostrar_login(request: Request):
    return templates.TemplateResponse(request, "login.html")
#Procesa el login con el usuario y contraseña
@app.post("/login")
def procesar_login(response: Response, usuario: str = Form(...), password: str = Form(...)):
    #Valida usuario y contraseña
    if usuario == ADMIN_USER and password == ADMIN_PASS:
        #Redirige a la ventana del panel 
        respuesta = RedirectResponse(url="/admin/dashboard", status_code=303)
        #crea una cookie
        respuesta.set_cookie(key="sesion_admin", value="activa", httponly=True)
        return respuesta
    return RedirectResponse(url="/login?error=true", status_code=303)

#Cierra la sesión y borra la cookie
@app.get("/logout")
def cerrar_sesion():
    respuesta = RedirectResponse(url="/", status_code=303)
    respuesta.delete_cookie("sesion_admin")
    return respuesta

#Ventana del panel de administración
@app.get("/admin/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    noticias = crud.obtener_todas_las_noticias_admin(db)    
    #renderiza la ventana
    return templates.TemplateResponse(request, "admin/dashboard.html", {"noticias": noticias})

#Mostrar el formulario para crear noticias
@app.get("/admin/crear")
def formulario_crear_noticia(request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    secciones = db.query(models.Seccion).all()
    return templates.TemplateResponse(request, "admin/crear.html", {"secciones": secciones})

#Guarda la noticia
@app.post("/admin/crear")
def guardar_nueva_noticia(
    titulo: str = Form(...), 
    contenido: str = Form(...),
    seccion_id: int = Form(...), 
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db), 
    _=Depends(verificar_admin_cookie)
):
    # Guardar el archivo físicamente en el servidor
    ruta_archivo_local = os.path.join(IMAGENES_DIR, imagen.filename)
    with open(ruta_archivo_local, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)
        
    # Ruta web que guardará en la base de datos
    imagen_url = f"/static/imagenes/{imagen.filename}"
    
    #llamada al CRUD
    crud.crear_noticia(db=db, titulo=titulo, contenido=contenido, imagen_url=imagen_url, seccion_id=seccion_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

#Muestra formulario de edición
@app.get("/admin/editar/{noticia_id}")
def formulario_editar_noticia(noticia_id: int, request: Request, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    #Error si no encuentra la noticia
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    secciones = db.query(models.Seccion).all()
    return templates.TemplateResponse(request, "admin/editar.html", {"noticia": noticia, "secciones": secciones})

#Guarda los nuevos datos
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
    # Si el usuario subió una nueva imagen, la guardamos; si no el CRUD mantiene la ruta vieja
    if imagen and imagen.filename:
        ruta_archivo_local = os.path.join(IMAGENES_DIR, imagen.filename)
        with open(ruta_archivo_local, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        imagen_url = f"/static/imagenes/{imagen.filename}"

    crud.modificar_noticia(db=db, noticia_id=noticia_id, titulo=titulo, contenido=contenido, imagen_url=imagen_url, seccion_id=seccion_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

#Borrado de noticia
@app.get("/admin/eliminar/{noticia_id}")
def borrar_noticia_ruta(noticia_id: int, db: Session = Depends(get_db), _=Depends(verificar_admin_cookie)):
    crud.eliminar_noticia(db=db, noticia_id=noticia_id)
    return RedirectResponse(url="/admin/dashboard", status_code=303)