import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facecontrol.settings')
django.setup()

from core.models import Alumno

cantidad = Alumno.objects.filter(encoding_facial__isnull=False).count()
print(f"Alumnos con encoding antes: {cantidad}")

Alumno.objects.update(encoding_facial=None)

cantidad_despues = Alumno.objects.filter(encoding_facial__isnull=False).count()
print(f"Alumnos con encoding después: {cantidad_despues}")
print("✅ Encodings eliminados. Ahora ejecuta: py test_registro.py")