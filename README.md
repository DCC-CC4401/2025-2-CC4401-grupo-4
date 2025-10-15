## ¿Qué es U-Clases?

**U-Clases** es una plataforma web desarrollada por estudiantes de la **Facultad de Ciencias Físicas y Matemáticas de la Universidad de Chile** que permite a alumnos ofrecer y solicitar clases particulares de forma sencilla, organizada y centralizada.

El proyecto está construido con **Django** y tiene como objetivo facilitar el intercambio de conocimiento entre pares, promoviendo el aprendizaje colaborativo y el desarrollo de habilidades docentes en la comunidad universitaria.

---

## ¿Para qué sirve U-Clases?

- **Estudiantes que necesitan ayuda**: pueden buscar tutores según su ramo, disponibilidad y tarifa.
- **Estudiantes que desean enseñar**: pueden ofrecer clases y gestionar sus solicitudes.
- La plataforma incluye funcionalidades como:
  - Filtros por especialidad, precio y horario.
  - Solicitud, confirmación o cancelación de clases.
  - Calificación posterior a la clase.
  - Notificaciones de nuevas solicitudes.

---

## ¿Qué problema resuelve U-Clases?

Actualmente, los estudiantes deben recurrir al foro de UCursos para encontrar o anunciar clases particulares, lo cual:

- Genera publicaciones desorganizadas.
- Reduce la visibilidad y accesibilidad.
- Dificulta la gestión de ofertas y solicitudes.

**U-Clases** resuelve esto ofreciendo un espacio exclusivo, claro y organizado, donde los estudiantes pueden gestionar clases desde una sola plataforma confiable.

---

## Tecnologías principales

- Django (Python)
- Node.js + npm
- HTML/CSS
- Tailwind CSS
- SQLite
- Git + GitHub

---

## 🚀 Cómo iniciar el proyecto

### Requisitos previos

- Python 3.8 o superior
- Node.js y npm (para Tailwind CSS)
- Git

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/DCC-CC4401/2025-2-CC4401-grupo-4.git
   cd 2025-2-CC4401-grupo-4
   ```

2. **Crear y activar el entorno virtual**
   
   Desde la raíz del proyecto (`2025-2-CC4401-grupo-4/`):
   
   En Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   En Linux/Mac:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias de Python**
   
   Desde la raíz del proyecto (`2025-2-CC4401-grupo-4/`):
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar dependencias de Node.js (para Tailwind)**
   
   Desde la raíz del proyecto (`2025-2-CC4401-grupo-4/`):
   ```bash
   npm install
   ```

5. **Aplicar migraciones**
   
   Desde la carpeta `uclases/`:
   ```bash
   cd uclases
   python manage.py migrate
   ```

6. **(Opcional) Cargar datos de prueba**
   
   Desde la carpeta `uclases/`:
   ```bash
   python manage.py seed
   ```

### Ejecutar el proyecto

1. **Iniciar el servidor de Django**
   
   Desde la carpeta `uclases/`:
   ```bash
   python manage.py runserver
   ```

2. **Iniciar Tailwind (en modo watch)**
   
   En otra terminal, desde la carpeta `uclases/`:
   ```bash
   npm run style
   ```

3. **Acceder a la aplicación**
   
   Abre tu navegador en: [http://localhost:8000](http://localhost:8000)

### Comandos útiles

- **Crear superusuario (admin):**
  
  Desde la carpeta `uclases/`:
  ```bash
  python manage.py createsuperuser
  ```

- **Acceder al panel de administración:**
  
  [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Guidelines para contribuir

Queremos mantener un código limpio, bien documentado y coherente. Si deseas contribuir al proyecto, por favor sigue estas directrices:

### Idioma

- La documentación debe escribirse en **español**.
- Los comentarios en el código deben estar en **inglés**.
- Los nombres de variables, funciones y clases deben estar en **inglés**.

### Estructura y patrones de diseño

- El proyecto sigue el patrón **MVT** (Model-View-Template).
- Se sigue la convención **PEP8** para el código Python.
- Se usa snake_case para nombres de carpetas, archivos y también para funciones en python
- Se usa PascalCase para nombres de clases en Django
- Se usa camelCase para funciones de javascript
- Las vistas usan **templates con HTML y CSS**, manteniendo la lógica en el backend.
- Se usa **Tailwind** para los estilos y componentes visuales reutilizables.
- Cada nueva funcionalidad debe ir acompañada de su respectiva **historia de usuario** y ser asignada en un sprint.

### Organización

- Los commits deben seguir la convención:
```
tipo([scope opcional]): descripción breve

Ejemplo:
feat(search-bar): agregar filtro de búsqueda por precio
fix(profile): corregir validación del formulario de registro
```
