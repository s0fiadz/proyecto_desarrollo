from encuesta.models import TipoIncidencia

# Verifica si hay datos en la tabla
print("Total de TiposIncidencia:", TipoIncidencia.objects.count())

# Verifica los nombres de las tablas que Django está usando
print("Tabla para TipoIncidencia:", TipoIncidencia._meta.db_table)

# Intenta crear uno manualmente
try:
    tipo = TipoIncidencia.objects.create(nombre="Test")
    print("Se pudo crear TipoIncidencia")
    tipo.delete()
except Exception as e:
    print("❌ Error:", e)