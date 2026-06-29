from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
import html

# FUNCIONES DE LECTURA

def obtener_noticias_carrusel(db: Session, limite_por_seccion: int = 2):
    """
    Obtiene las noticias para el carrusel de la página de inicio.
    """
    #Consulta a la base y seleccion de las 2 notas más recientes de cada sección
    return db.query(models.Noticia)\
             .order_by(models.Noticia.visitas.desc())\
             .limit(limite_por_seccion * 2)\
             .all()

#Obtiene las 6 noticias más recientes y las enlista
def obtener_noticias_recientes(db: Session, limite: int = 6):
    """
    Trae las últimas publicaciones ordenadas de forma cronológica descendente
    """
    return db.query(models.Noticia)\
             .order_by(models.Noticia.id.desc())\
             .limit(limite)\
             .all()

def obtener_noticia_y_contar_visita(db: Session, noticia_id: int):
    """
    Busca una noticia por su ID y le aumenta el contador de visitas
    """
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        noticia.visitas += 1
        db.commit()
        db.refresh(noticia)
    return noticia

def obtener_todas_las_noticias_admin(db: Session):
    """
    Trae todas las noticias ordenadas por la más reciente
    """
    return db.query(models.Noticia).order_by(models.Noticia.fecha_modificacion.desc()).all()


def obtener_noticias_por_seccion(db: Session, seccion_slug: str):
    """
    Filtra las noticias que pertenecen a una sección específica
    """
    return db.query(models.Noticia)\
             .join(models.Seccion)\
             .filter(models.Seccion.slug == seccion_slug)\
             .order_by(models.Noticia.fecha_modificacion.desc())\
             .all()



# FUNCIONES  CREATE, UPDATE y DELETE


def crear_noticia(db: Session, titulo: str, contenido: str, imagen_url: str, seccion_id: int):
    #Protección contrs scripts
    titulo_limpio = html.escape(titulo.strip())
    contenido_limpio = html.escape(contenido.strip())
    
    nueva_noticia = models.Noticia(
        titulo=titulo_limpio,
        contenido=contenido_limpio,
        imagen_url=imagen_url.strip(),
        seccion_id=seccion_id,
        visitas=0
    )
    db.add(nueva_noticia)
    db.commit()
    db.refresh(nueva_noticia)
    return nueva_noticia

def modificar_noticia(db: Session, noticia_id: int, titulo: str, contenido: str, imagen_url: str, seccion_id: int):
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        noticia.titulo = html.escape(titulo.strip())
        noticia.contenido = html.escape(contenido.strip())
        noticia.seccion_id = seccion_id
        if imagen_url:
            noticia.imagen_url = imagen_url.strip()
        
        db.commit()
        db.refresh(noticia)
    return noticia


def eliminar_noticia(db: Session, noticia_id: int):
    """
    Elimina permanentemente una noticia de la base de datos usando su ID.
    """
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        db.delete(noticia)
        db.commit()
        return True
    return False