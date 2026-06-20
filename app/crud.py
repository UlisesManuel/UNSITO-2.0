from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

# ==========================================
# 1. LOGIC FOR THE CAROUSEL & RECENT FEED
# ==========================================

def obtener_noticias_recientes(db: Session, limite: int = 6):
    """
    Trae las últimas noticias globales ordenadas por fecha de creación.
    Útil para el feed principal debajo del carrusel.
    """
    return db.query(models.Noticia)\
             .order_by(models.Noticia.fecha_creacion.desc())\
             .limit(limite)\
             .all()

def obtener_noticias_carrusel(db: Session, limite_por_seccion: int = 2):
    """
    Trae las 1 o 2 noticias más recientes o modificadas de CADA sección.
    Utiliza una ventana (Window Function) para particionar y filtrar eficientemente.
    """
    # Creamos una subconsulta que numera las noticias dentro de cada sección ordenadas por modificación
    subquery = db.query(
        models.Noticia,
        func.row_number().over(
            partition_by=models.Noticia.seccion_id,
            order_by=models.Noticia.fecha_modificacion.desc()
        ).label("row_num")
    ).subquery()

    # Filtramos para quedarnos solo con las primeras (1 o 2) de cada sección
    noticias_filtradas = db.query(models.Noticia)\
                           .select_entity_from(subquery)\
                           .filter(subquery.c.row_num <= limite_por_seccion)\
                           .all()
    return noticias_filtradas

def obtener_noticias_por_seccion(db: Session, seccion_slug: str):
    """
    Trae todas las noticias pertenecientes a una sección específica usando su slug.
    """
    return db.query(models.Noticia)\
             .join(models.Seccion)\
             .filter(models.Seccion.slug == seccion_slug)\
             .order_by(models.Noticia.fecha_creacion.desc())\
             .all()

# ==========================================
# 2. LOGIC FOR THE DETAIL VIEW & METRICS
# ==========================================

def obtener_noticia_y_contar_visita(db: Session, noticia_id: int):
    """
    Busca una noticia por su ID e incrementa su contador de visualizaciones en +1.
    """
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        noticia.visitas += 1
        db.commit()
        db.refresh(noticia)
    return noticia

# ==========================================
# 3. ADMINISTRATOR CRUD (Altas, Bajas, Cambios)
# ==========================================

def crear_noticia(db: Session, titulo: str, contenido: str, imagen_url: str, seccion_id: int):
    """
    Da de alta una nueva noticia en el sistema.
    """
    nueva_noticia = models.Noticia(
        titulo=titulo,
        contenido=contenido,
        imagen_url=imagen_url,
        seccion_id=seccion_id
    )
    db.add(nueva_noticia)
    db.commit()
    db.refresh(nueva_noticia)
    return nueva_noticia

def modificar_noticia(db: Session, noticia_id: int, titulo: str, contenido: str, imagen_url: str, seccion_id: int):
    """
    Modifica los datos de una noticia existente.
    """
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        noticia.titulo = titulo
        noticia.contenido = contenido
        if imagen_url:  # Solo la actualiza si el administrador subió una nueva
            noticia.imagen_url = imagen_url
        noticia.seccion_id = seccion_id
        db.commit()
        db.refresh(noticia)
    return noticia

def eliminar_noticia(db: Session, noticia_id: int):
    """
    Elimina por completo una noticia utilizando su ID.
    """
    noticia = db.query(models.Noticia).filter(models.Noticia.id == noticia_id).first()
    if noticia:
        db.delete(noticia)
        db.commit()
        return True
    return False

def obtener_todas_las_noticias_admin(db: Session):
    """
    Lista todas las noticias con sus métricas de visitas para el Dashboard del Administrador.
    """
    return db.query(models.Noticia).order_by(models.Noticia.fecha_creacion.desc()).all()