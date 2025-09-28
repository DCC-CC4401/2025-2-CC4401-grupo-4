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
- HTML/CSS
- Tailwind
- SQLite
- Git + GitHub

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
