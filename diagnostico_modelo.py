import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facecontrol.settings')
django.setup()

import numpy as np
from deepface import DeepFace
from core.models import Alumno
from core.facial.registro import binario_a_encoding

# 1. Ver el encoding guardado
alumno = Alumno.objects.filter(encoding_facial__isnull=False).first()
encoding_guardado = binario_a_encoding(alumno.encoding_facial)

print("=" * 60)
print("ENCODING GUARDADO")
print("=" * 60)
print(f"Alumno: {alumno}")
print(f"Shape: {encoding_guardado.shape}")
print(f"Dtype: {encoding_guardado.dtype}")
print(f"Norma: {np.linalg.norm(encoding_guardado):.4f}")
print(f"Rango: min={encoding_guardado.min():.4f}, max={encoding_guardado.max():.4f}")
print(f"Primeros 5: {encoding_guardado[:5]}")

# 2. Extraer encoding de la misma foto de referencia
print("\n" + "=" * 60)
print("EXTRACCIÓN DE LA MISMA FOTO DE REFERENCIA")
print("=" * 60)

ruta_foto = alumno.foto_referencia.path
print(f"Foto: {ruta_foto}")

representaciones = DeepFace.represent(
    img_path=ruta_foto,
    model_name='Facenet',
    detector_backend='opencv',
    enforce_detection=False
)

if representaciones:
    encoding_nuevo = np.array(representaciones[0]['embedding'])
    print(f"Shape: {encoding_nuevo.shape}")
    print(f"Dtype: {encoding_nuevo.dtype}")
    print(f"Norma: {np.linalg.norm(encoding_nuevo):.4f}")
    print(f"Rango: min={encoding_nuevo.min():.4f}, max={encoding_nuevo.max():.4f}")
    print(f"Primeros 5: {encoding_nuevo[:5]}")

    # 3. Comparar la misma foto consigo misma
    distancia = np.linalg.norm(encoding_guardado - encoding_nuevo)
    print(f"\n🔍 Distancia entre la misma foto: {distancia:.4f}")

    if distancia < 0.01:
        print("✅ El encoding guardado coincide con el recién extraído")
        print("   El problema está en la cámara en vivo")
    elif distancia < 0.5:
        print("⚠️  Hay pequeña variación, pero debería reconocer")
    else:
        print("❌ El encoding guardado NO coincide con el de la misma foto")
        print("   El problema está en cómo se guardó o se carga")
else:
    print("❌ No se detectó rostro en la foto de referencia")

print("=" * 60)