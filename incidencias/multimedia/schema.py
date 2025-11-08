
from pymongo import MongoClient
client = MongoClient('mongodb+srv://robuc_db_user:Arrob2909@cluster0.ghii80n.mongodb.net/')#usa tu string de conexión de MongoDB Atlas
db = client['universidad']

# Definir el esquema de validación para la colección "estudiantes"
validator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['nombre', 'edad', 'direccion', 'asignaturas'],
        'properties': {
            'nombre': {
                'bsonType': 'string',
                'description': 'Debe ser un string y es obligatorio'
            },
            'edad': {
                'bsonType': 'int',
                'minimum': 16,
                'maximum': 120,
                'description': 'Debe ser un entero entre 16 y 120'
            },
            'direccion': {
                'bsonType': 'object',
                'required': ['calle', 'comuna', 'region'],
                'properties': {
                    'calle': {'bsonType': 'string'},
                    'comuna': {'bsonType': 'string'},
                    'region': {'bsonType': 'string'}
                }
            },
            'asignaturas': {
                'bsonType': 'array',
                'items': {'bsonType': 'objectId'},
                'description': 'Debe ser arreglo de ObjectIds'
            }
        }
    }
}

# Para validar prueba creando la colección
try:
    db.create_collection('estudiantes', validator={'$jsonSchema': validator['$jsonSchema']})
except Exception as e:
    print("La colección ya existe o hubo un error:", e)

