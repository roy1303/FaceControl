import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facecontrol.settings')
django.setup()

import cv2
from deepface import DeepFace

from core.facial.reconocimiento import (
    obtener_encodings_alumnos,
    encontrar_alumno,
    registrar_asistencia
)

# ============================================================
# CONFIGURACIÓN
# ============================================================
CAMARA_INDEX = 1
DETECTOR = 'opencv'
MODELO = 'Facenet'
ANALIZAR_CADA = 10
UMBRAL = 0.7  # <-- Ajusta aquí: 0.3 estricto, 0.6 tolerante

# ============================================================
# CARGA INICIAL
# ============================================================
print("Cargando encodings de alumnos...")
encodings_alumnos = obtener_encodings_alumnos()
print(f"Alumnos con encoding: {len(encodings_alumnos)}")

if len(encodings_alumnos) == 0:
    print("⚠️  No hay alumnos con encoding. Ejecuta primero: py test_registro.py")
    exit()

# ============================================================
# ABRIR CÁMARA
# ============================================================
cap = cv2.VideoCapture(CAMARA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

print(f"Detector: {DETECTOR} | Modelo: {MODELO} | Umbral: {UMBRAL}")
print("Presiona 'q' para salir")

# ============================================================
# BUCLE PRINCIPAL
# ============================================================
frame_count = 0
ultimo_resultado = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el fotograma")
        break

    frame_count += 1

    # Analizar solo cada N frames
    if frame_count % ANALIZAR_CADA == 0:
        try:
            representaciones = DeepFace.represent(
                img_path=frame,
                model_name=MODELO,
                detector_backend=DETECTOR,
                enforce_detection=False,
               
            )

            ultimo_resultado = None

            for rep in representaciones:
                area = rep['facial_area']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']
                encoding_actual = rep['embedding']

                # Ignorar rostros muy pequeños (falsos positivos)
                if w < 30 or h < 30:
                    continue

                # Buscar coincidencia
                alumno, distancia = encontrar_alumno(
                    encoding_actual,
                    encodings_alumnos,
                    umbral=UMBRAL
                )

                # Diagnóstico: mostrar siempre la distancia
                if alumno:
                    print(f"✅ {alumno.nombre} {alumno.apellido_paterno} | distancia={distancia:.4f}")
                else:
                    print(f"❓ Desconocido | distancia={distancia:.4f}")

                if alumno:
                    creado, registro = registrar_asistencia(
                        alumno, confianza=float(distancia)
                    )
                    if creado:
                        print(f"   📝 Registro creado: {registro.tipo}")
                    ultimo_resultado = (x, y, w, h, alumno, distancia, True)
                else:
                    ultimo_resultado = (x, y, w, h, None, distancia, False)

        except Exception as e:
            print(f"Error: {e}", end="\r")

    # Dibujar el último resultado
    if ultimo_resultado:
        x, y, w, h, alumno, distancia, reconocido = ultimo_resultado
        color = (0, 255, 0) if reconocido else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        if reconocido and alumno:
            texto = f"{alumno.nombre} ({distancia:.2f})"
        else:
            texto = f"Desconocido ({distancia:.2f})"

        cv2.putText(frame, texto, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('Face Control - Reconocimiento', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()