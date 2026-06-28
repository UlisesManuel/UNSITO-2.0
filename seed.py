from app.database import SessionLocal, engine, Base
from app.models import Seccion

def poblar_secciones():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        secciones_base = [
            {"nombre": "Academia", "slug": "academia"},
            {"nombre": "Cultura", "slug": "cultura"},
            {"nombre": "Deportes", "slug": "deportes"},
            {"nombre": "Avisos Oficiales", "slug": "avisos-oficiales"}
        ]
        
        print("Insertando secciones base...")
        for sec in secciones_base:
            existe = db.query(Seccion).filter(Seccion.slug == sec["slug"]).first()
            if not existe:
                nueva_seccion = Seccion(nombre=sec["nombre"], slug=sec["slug"])
                db.add(nueva_seccion)
                print(f"-> Seccion '{sec['nombre']}' agregada con éxito.")
            else:
                print(f"-> La sección '{sec['nombre']}' ya existe en la base de datos.")
                
        db.commit()
        print("\n¡Proceso terminado con éxito!")
        
    except Exception as e:
        print(f"Ocurrió un error al poblar la BD: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    poblar_secciones()