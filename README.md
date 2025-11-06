# 👋 Bienvenid@s al repositorio del proyecto

---

# 🛠 Requisitos previos

Antes de comenzar, asegúrate de:

- Tener instalada la versión **Python 3.11**
- Instalar las dependencias desde tu consola de preferencia (teniendo activado tu entorno):

```
pip install -r requirements.txt
```

# 🌱 Clonar el repositorio
```
cd (ingresa la dirección donde dejarás el proyecto)
git clone https://github.com/s0fiadz/proyecto_desarrollo.git
```
# 👤 Configurar identidad local en Git
Antes de hacer tu primer commit, configura tu nombre y correo para que Git registre correctamente tus contribuciones :
```
git config user.name "tu_usuario_en_GitHub"
git config user.email "tu_correo_vinculado_en_GitHub@ejemplo.com"
```
(recuerda usar tus mismas credenciales que tienes en tu cuenta de GitHub)

# 🗂️ Base de datos
1. Primero, deben meterse a la carpeta de donde tienen clonado el git, meterse a cada una de las aplicaciones, y borrar las migraciones (ej: core -> migrations -> borrar todo menos __pycache__ y __init__). Deben hacer en cada una de las aplicaciones creadas.
2. Deben eliminar la base de datos que ya tenían y crean una nueva con el mismo nombre: 'proyectoweb'
3. Luego se van a la consola y hacen 'python manage.py makemigrations' y luego 'python manage.py migrate'
4. Luego insertan estos datos en la base de datos:
```
insert into auth_group VALUES(1, 'Admin')
insert into auth_group VALUES(2, 'Direccion')
insert into auth_group VALUES(3, 'Departamento')
insert into auth_group VALUES(4, 'Territorial')
insert into auth_group VALUES(5, 'Cuadrilla')
```
5. Luego creen el super usuario con 'python manage.py createsuperuser'
6. Una vez creado, ingresan esto en la base de datos:
```
insert into registration_profile VALUES(0, 'Default','Default', 88738473, 1,1)
```

# 🌿 Flujo de Trabajo con Git

| Acción                                    | Comando                                                       |
| ----------------------------------------- | ------------------------------------------------------------- |
| **Actualizar la rama principal**          | `git checkout main`<br>`git pull origin main`                 |
| **Crear una nueva rama para tu feature**  | `git checkout -b feature/nombre-de-la-feature`                |
| **Sincronizar con los cambios del main**  | `git fetch origin`                                            |
| **Guardar tus cambios**                   | `git add .`<br>`git commit -m "Descripción clara del cambio"` |
| **Subir tu rama y crear un Pull Request** | `git push -u origin feature/nombre-de-la-feature`             |

nombre-de-la-feature: ingresar nombre simple y breve de la tarea que estas haciendo 


# ✅ Buenas prácticas
- No trabajar directamente en main
- Hacer commits de tus tareas y descriptivos
- Revisar que todo esté funcionando antes de subir
- Mantener la documentación actualizada
- Avisar cuando se termine de usar una rama (cuando se haya completado la tarea)

# 📄 Archivo .gitignore
Este proyecto ignora los siguientes archivos y carpetas:
```
/settings.py
__pycache__/
*.py[cod]
```
No pueden cambiar nada de esta carpeta, si quieren agregar algo, consultar primero
