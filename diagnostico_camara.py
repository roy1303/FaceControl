import cv2
import numpy as np

# Probar todas las combinaciones posibles
backends = [
    ("CAP_DSHOW", cv2.CAP_DSHOW),
    ("CAP_MSMF", cv2.CAP_MSMF),
    ("CAP_ANY", cv2.CAP_ANY),
]

for nombre, backend in backends:
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index, backend)
        if not cap.isOpened():
            cap.release()
            continue

        # Intentar leer varios frames (a veces el primero sale negro)
        frames_ok = 0
        brillo = 0
        for _ in range(10):
            ret, frame = cap.read()
            if ret and frame is not None:
                frames_ok += 1
                brillo += frame.mean()
        
        if frames_ok > 0:
            brillo_promedio = brillo / frames_ok
            print(f"✅ {nombre}, index={index}: {frames_ok}/10 frames, brillo={brillo_promedio:.1f}")
            
            # Mostrar si el brillo es aceptable
            if brillo_promedio < 5:
                print(f"   ⚠️  IMAGEN NEGRA (brillo muy bajo)")
            elif brillo_promedio < 30:
                print(f"   ⚠️  IMAGEN MUY OSCURA")
            else:
                print(f"   ✅ Imagen con contenido visible")
        
        cap.release()

print("\nDiagnóstico terminado")