from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Seccion(Base):
    __tablename__ = "secciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)  # Ej: "Deportes", "Cultura"
    slug = Column(String, unique=True, index=True)    # Ej: "act-depo", "act-cul"

    # Relación uno a muchos con Noticias
    noticias = relationship("Noticia", back_populates="seccion")


class Noticia(Base):
    __tablename__ = "noticias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)
    imagen_url = Column(String, nullable=True)  # Nombre del archivo en /static/Noticias/
    
    # Manejo de fechas para ordenamiento cronológico y actualizaciones
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Contador de visualizaciones para las métricas del administrador
    visitas = Column(Integer, default=0)
    
    # Clave foránea hacia Secciones
    seccion_id = Column(Integer, ForeignKey("secciones.id"))

    seccion = relationship("Seccion", back_populates="noticias")