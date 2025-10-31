# 👋 Bienvenid@s al repositorio del proyecto

---

# 🛠 Requisitos previos

Antes de comenzar, asegúrate de:

- Tener instalada la versión **Python 3.11**
- Instalar las dependencias desde tu consola de preferencia (teniendo activado tu entorno):

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


# 🌱 Clonar el repositorio
```
cd (ingresa la dirección donde dejarás el proyecto)
git clone https://github.com/s0fiadz/Desarrollo_App.git
```


# 🌿 Crear una rama para trabajar
Las ramas permiten trabajar por separado en equipo.
No ocupen el nombre main para no confundir con la rama principal.
```
git branch nombre-de-la-rama
git checkout nombre-de-la-rama
```

Si deseas eliminar una rama por algún motivo, debes comunicarlo a la encargada del Git.


# 📦 Hacer cambios y commitear
```
git add .
git commit -m "inserte_mensaje"
```

El mensaje debe incluir una palabra o frase clave que describa lo que se modificó.


# 🔄 Sincronizar con el repositorio remoto
Antes de hacer push, actualiza tu rama local:
```
git pull origin main
git push origin nombre-de-la-rama
```
"git pull origin main" : nos sirve para actualizar tu rama local "main" con lo que está en el GitHub.

# 🔁 Actualización de cambios desde tu rama
Este comando fusiona los cambios de tu rama con la rama main, es decir, si estas trabajando en una rama llamada "ejemplo", al ejecutar:
```
git checkout main
git merge nombre-de-la-rama
git push origin main
```
Git traerá todos los cambios que estén en la rama "ejemplo" y los integrara en el main
Recuerda: no puedes hacer merge sin haber commiteado tus cambios.

"git checkout main": cambiamos a la rama main
"git merge nombre-de-la-rama": combinamos los cambio de tu rama
"git push origin main": subimos todo al GitHub


# ✅ Buenas prácticas
- No trabajar directamente en main
- Hacer commits frecuentes y descriptivos
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
