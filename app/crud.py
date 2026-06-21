from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
import html

# ==============================================================================
# FUNCIONES DE LECTURA (ADMIN Y FRONT)
# ==============================================================================

def obtener_todas_las_noticias_admin(db: Session):
    """
    Trae absolutamente todas las noticias ordenadas por la más reciente.
    Ideal para la tabla del panel de administración.
    """
    return db.query(models.Noticia).order_by(models.Noticia.fecha_modificacion.desc()).all()


def obtener_noticias_por_seccion(db: Session, seccion_slug: str):
    """
    Filtra las noticias que pertenecen a una sección específica usando su slug.
    """
    return db.query(models.Noticia)\
             .join(models.Seccion)\
             .filter(models.Seccion.slug == seccion_slug)\
             .order_by(models.Noticia.fecha_modificacion.desc())\
             .all()


# ==============================================================================
# FUNCIONES DE ESCRITURA (CUD - CREATE, UPDATE, DELETE)
# ==============================================================================

def crear_noticia(db: Session, titulo: str, contenido: str, imagen_url: str, seccion_id: int):
    # Sanitizar textos eliminando etiquetas dañinas
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