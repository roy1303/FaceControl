import os
import django

# Configurar Django para usar el script standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facecontrol.settings')
django.setup()

from core.models import Alumno
from core.facial.registro import registrar_alumno

# Procesar todos los alumnos que tengan foto pero no encoding
alumnos_sin_encoding = Alumno.objects.filter(
    foto_referencia__isnull=False,
    encoding_facial__isnull=True
)

print(f"Alumnos sin encoding: {alumnos_sin_encoding.count()}")

for alumno in alumnos_sin_encoding:
    registrar_alumno(alumno)