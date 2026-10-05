import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facecontrol.settings')
django.setup()

from core.models import RegistroAsistencia
from core.facial.exportar import exportar_asistencias_a_excel

# Obtener todos los registros
registros = RegistroAsistencia.objects.all().select_related('alumno', 'alumno__grupo')

print(f"Total de registros: {registros.count()}")

if registros.count() == 0:
    print("⚠️  No hay registros. Toma asistencia primero con reconocimiento_vivo.py")
    exit()

ruta = exportar_asistencias_a_excel(registros)
print(f"✅ Archivo generado: {os.path.abspath(ruta)}")