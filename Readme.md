## EL UNSITO 2.0 - Gaceta Universitaria Digital

¡Bienvenido a **EL UNSITO 2.0** Un sistema web full-stack, responsiva y de alto rendimiento diseñada como el sistema de gaceta informativa oficial para la comunidad universitaria. El sistema implementa un portal de lectura automatizado y un módulo de administración privado blindado para la gestión del contenido.

## Descripción del Proyecto
EL UNSITO 2.0 es una aplicación modular que resuelve la necesidad de difundir proyectos, cultura, academia y avisos institucionales. Permite al público general consumir notas con un orden cronológico y de popularidad, mientras provee a los administradores un panel de control seguro con persistencia física de archivos multimedia e interacciones dinámicas en tiempo real con la base de datos sin depender de frameworks de JavaScript pesados en el cliente.

## Arquitectura del Sistema
El proyecto sigue un patrón arquitectónico de **Renderizado en el Servidor (SSR)** combinado con el patrón **MVC (Modelo-Vista-Controlador)** adaptado al ecosistema moderno de FastAPI:

_________________________________________________
                FRONTEND (Vistas)                    
     HTML5 + CSS3 + Tailwind CSS + Jinja2              
__________________________________▲______________
                   │              |
            Peticiones HTTP     Renderizado HTML
                   │              │
___________________▼_____________________________
                BACKEND (FastAPI)                    
   Enrutamiento + Seguridad + Inyección Dependencias    
_________________________________________________
                   |              │
                Operaciones     Resultados
                ORM CRUD       de Consulta
                   │              │
___________________▼______________|______________
           BASE DE DATOS & PERSISTENCIA                
     SQLite + SQLAlchemy ORM + Almacén Estático 
_________________________________________________       


## Frontend:
Diseñado con un estilo moderno, responsivo y conpletamente perzonalizado utilizando Tailwind CSS mediante su arquitectura utility-first. El corazoón del proyecto usa jinja2 para procesar bucles, condicionales e inyección de datos de manera segura directamente desde el servidor, mitigando vulnerabilidades.

## Backend
Desarrollado sobre el FastAPI, que se encarga de procesar las solicitudes concurrentes, gestionar los esquemas de validación multipart para la carga de archivos binarios y valida las sesiones administrativas.

## Manejo de datos :
Gestionada a través de SQLAlchemy ORM conectado a un motor relacional SQLite. Las imágenes son almacenadas físicamente en el disco en el directorio de recursos estáticos controlado por FastAPI, registrandolos mendiante la ruta relativa en la base de datos para ahorrar rendimiento.

## TECNOLOGÍAS UTILIZADAS
En esta proyecto se manejaron distintas tecnologías para garantizar la estabilidad y funcionalidad del entorno, se espesifican las siguientes versiones de software:
°Lenguaje de programación: Python v3.13+
°Framework Web: FastAPI v0.115+
°Servidor ASGI: Uvicorn v0.34+
°Motor de Plantillas: Jinja2 v3.1+
°Base de Datos: SQLAlchemy v2.0 /SQLite v3+
°Procesamiento de formularios: Python-Multipart v0.0.20+
°Estilos: Tailwind CSS v3.4+ (vía CDN/Play CDN para desarrollo)
°Servidor de desarrollo: Uvicorn


## ESTRUCUTURA DEL PROYECTO ##

UNSITOS_2.0/
├── app/
│   ├── main.py                 # Inicialización, dependencias, middlewares y rutas FastAPI
│   ├── models.py               # Definición de tablas relacionales de SQLAlchemy (Noticia, Seccion)
│   ├── crud.py                 # Consultas e interacciones directas con la BD (Create, Read, Update, Delete)
│   ├── database.py             # Configuración del motor SQLite y generador de sesiones locales
│   ├── __init__.py             # Inicializador del módulo Python de la aplicación
│   ├── static/                 # Recursos estáticos servidos de forma segura por el backend
│   │   ├── CSS/                # Estilos personalizados e integraciones de Tailwind(Util si lo ejecutaramos con internet)
│   │   ├── imagenes/           # Almacén de imágenes generales del sistema
│   │   ├── JS/                 # Scripts interactivos de la aplicación frontend
│   │   │   ├── carrousel.js    # Manejo dinámico del carrusel de la página de inicio
│   │   │   ├── login.js        # Validaciones e interacciones de la pantalla de acceso
│   │   │   ├── vistaCrear.js   # Pre-visualización de la imágen al crear noticia
│   │   │   └── vistaEditar.js  # Pre-visualización de la imágen al crear noticia
│   │   └── Noticias/           # Carpeta física donde se guardan las imágenes cargadas de los artículos
│   └── templates/              # Plantillas HTML estructuradas y procesadas por Jinja2
│       ├── index.html          # Página de inicio pública (Carrusel + Publicaciones Recientes)
│       ├── seccion.html        # Listado dinámico filtrado por categoría editorial (Academia, Cultura...)
│       ├── noticia.html        # Vista extendida para la lectura completa y conteo de visitas del artículo
│       ├── login.html          # Interfaz de acceso administrativo
│       └── admin/              # Vistas protegidas del Panel Administrativo
│           ├── dashboard.html  # Panel central con la tabla de gestión de todas las noticias
│           ├── crear.html      # Formulario web estructurado para la inserción de nuevas noticias
│           └── editar.html     # Formulario dinámico con persistencia de datos previos para modificar noticias
├── Readme.md                   # Documentación técnica completa del sistema
├── seed.py                     # Script automatizado para poblar el catálogo de secciones base
└── unsito.db                   # Base de datos relacional SQLite generada localmente en desarrollo

## ENDPOINT DE LA API ##

### Módulo público
Método  |  Endpoint         |                          Descripción                                                                     | Paramentros
-----------------------------------------------------------------------------------------------------------------------------------------
GET     | `/`               | Renderiza la página de inicio pública con las noticias más leídas (Carrusel) y los últimos lanzamientos. | Ninguno
POST    |`/Seccion/{slug}`  | Filtra de manera dinámica y despliega las publicaciones pertenecientes a una categoría.                  | slug (str)
GET     | `/noticia/{noticia_id}`| Muestra el artículo completo e incrementa de forma automática en +1 el contador de visitas en la BD.| noticia_id (int)

### Módulo de Autenticación
Método  |  Endpoint |                          Descripción                                                                        | Paramentros
-----------------------------------------------------------------------------------------------------------------------------------------
GET     | `/login`  | Renderiza la interfaz gráfica de acceso para administradores construida con utilidades de Tailwind.         | error (bool, opcional)
POST    | `/login`  | Procesa las credenciales. Si son válidas, inyecta una Cookie cifrada segura; si no, redirige con estado 333.| Form(usuario, password)
GET     | `/logout` | Destruye la sesión de usuario activa eliminando las cookies del cliente y redirige a la raíz del sitio.     | ninguno

### Módulo de Administración
Método  |  Endpoint               |                          Descripción                                                                       | Paramentros
-----------------------------------------------------------------------------------------------------------------------------------------------
GET     | `/admin/dashboard`      | Panel de control central. Lista en forma de tabla todas las notas y provee acceso a operaciones de gestión.| Ninguno
GET     | `/admin/crear`          | Renderiza el formulario web con codificación multipart para la inserción de nuevos artículos.              | Ninguno
POST    | `/admin/crear`          | Recibe los textos y la imagen binaria, escribe el archivo en el servidor y crea el registro en la BD.   | Form(titulo,contenido,seccion_id)+UploadFile(imagen)
GET     | `/admin/editar/{id}`    | Despliega el formulario de edición con los valores actuales cargados dinámicamente.                        | id (int)
POST    | `/admin/editar/{id}`    | Modifica los datos del artículo. Si no se envía una imagen nueva, conserva de forma íntegra el archivo anterior.| id (int) + Datos de Formulario
POST    | `//admin/eliminar/{id}` | Remueve de manera permanente la noticia seleccionada de la base de datos relacional.                       | id (int)

## Instrucciones de Instalación y Ejecución
Para poder usar **EL UNSITO** seguir cuidadosamente los siguientes pasos:

# 1. Clonar el Código Fuente de mi repositorio
Abre tu terminal favorita y descarga el repositorio:

`git clone [https://github.com/UlisesManuel/UNSITO-2.0.git]`
`cd UNSITO-2.0`

# 2. Creación e Instalación de Dependencias
Asegúrarse de contar con Python instalado globalmente. Ejecutar el comando de instalación de paquetes de Python (pip) para montar los módulos necesarios listados en la arquitectura:

`pip install fastapi uvicorn sqlalchemy jinja2 python-multipart`

# 3. Configuración e Inicialización de la Base de Datos
Antes de ejecutar el servidor, se debe construir el esquema relacional y poblar los catálogos base (Academia, Cultura, Deportes, Avisos Oficiales). Ejecuta el script de inicialización:

`python seed.py`

## 4. Lanzamiento del Servidor en Entorno de Desarrollo
Poner en marcha el servidor de aplicaciones ASGI utilizando Uvicorn con la bandera de recarga, la cual vigila cambios en los archivos y refresca el proceso automáticamente:

`python -m uvicorn app.main:app --reload`

Abre el navegador de preferencia y accede a la dirección de bucle local para interactuar con la plataforma:

`http://127.0.0.1:8000`


##  CREDENSIALES DE PRUEBA PARA LAS VISTAS DE ADMINISTRACIÓN ##

Para acceder a las vistas administrativas, crear publicaciones con imágenes físicas y realizar modificaciones, autentícate en /login utilizando:
    **Usuario**: admin
    **Contraseña**: admin123



## VIDEO-TUTORIAL DE LAS FUNCIONALIDADES DEL SISTEMA
https://drive.google.com/file/d/1tGKHx_W20p5V6zOJ6KvvCNl2R7MP4Qzn/view?usp=drive_link