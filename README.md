# 👋 Bienvenid@s al repositorio del proyecto

---

# 🛠 Requisitos previos

Antes de comenzar, asegúrate de:

- Tener instalada la versión **Python 3.11**

# 🌱 Clonar el repositorio
```
cd (ingresa la dirección donde dejarás el proyecto)
git clone https://github.com/s0fiadz/proyecto_desarrollo.git
```
Instala las dependencias desde tu consola de preferencia (teniendo activado tu entorno):
```
pip install -r requirements.txt
```
# 👤 Configurar identidad local en Git
Antes de hacer tu primer commit, configura tu nombre y correo para que Git registre correctamente tus contribuciones :
```
git config user.name "tu_usuario_en_GitHub"
git config user.email "tu_correo_vinculado_en_GitHub@ejemplo.com"
```
(recuerda usar tus mismas credenciales que tienes en tu cuenta de GitHub)

# 🗂️ Base de datos
1. Primero, deben crear la base de datos que se llame 'proyectoweb'
2. Se van a la consola de la carpeta del proyecto y hacen 'python manage.py migrate'
3. Luego en la misma consola pegan 'python manage.py shell'
Esto abrirá una consola interactiva donde tienen que pegar una por una las siguientes líneas (presionar enter despues de cada línea pegada):
```
from django.contrib.auth.models import Group
Group.objects.create(name='Admin')
Group.objects.create(name='Direccion')
Group.objects.create(name='Departamento')
Group.objects.create(name='Territorial')
Group.objects.create(name='Cuadrilla')
```
Para salir simplemente pongan 'exit()'

4. Luego creen el super usuario con 'python manage.py createsuperuser'
5. Una vez creado, ingresan esto en la base de datos:
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
- Si vas a cambiar algo de la base de datos recuerda hacer un 'python manege.py makemigrations' y luego un 'python manage.py migrate'

# 📄 Archivo .gitignore
Este proyecto ignora los siguientes archivos y carpetas:
```
**/__pycache__/
*.py[cod]
*.pyc
__pycache__/
```
No pueden cambiar nada de esta carpeta, si quieren agregar algo, consultar primero
