from app.database import SessionLocal, engine, Base
from app.models import Seccion

def poblar_secciones():
    # Asegura que las tablas estén creadas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Secciones base correspondientes a tus páginas del UNSITO
        secciones_base = [
            {"nombre": "Actividades Académicas", "slug": "ActAca"},
            {"nombre": "Actividades Culturales", "slug": "ActCul"},
            {"nombre": "Actividades Deportivas", "slug": "ActDepo"}
        ]
        
        print("Insertando secciones base...")
        for sec in secciones_base:
            # Verificar si ya existe para no duplicar
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