import cv2
from deepface import DeepFace

# Configuración
CAMARA_INDEX = 1
DETECTOR = 'opencv'  # 'opencv' es el más rápido; 'mtcnn' es intermedio
ANALIZAR_CADA = 5    # Analizar 1 de cada 5 frames

cap = cv2.VideoCapture(CAMARA_INDEX, cv2.CAP_DSHOW)

# Forzar resolución 640x480 para mejor rendimiento
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

print(f"Detector: {DETECTOR} | Analizando cada {ANALIZAR_CADA} frames")
print("Presiona 'q' para salir")

frame_count = 0
ultimo_rectangulo = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el fotograma")
        break

    frame_count += 1

    # Analizar solo cada N frames
    if frame_count % ANALIZAR_CADA == 2:
        try:
            rostros = DeepFace.extract_faces(
                img_path=frame,
                detector_backend=DETECTOR,
                enforce_detection=False
            )

            ultimo_rectangulo = None  # Resetear antes de procesar

            for rostro in rostros:
                area = rostro['facial_area']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']
                confianza = rostro.get('confidence', 0)

                # Filtrar detecciones falsas (confianza baja)
                if confianza > 0.5 and w > 30 and h > 30:
                    ultimo_rectangulo = (x, y, w, h)
                    print(f"Rostro detectado (confianza={confianza:.2f})", end="\r")
                else:
                    print(f"Filtrado: confianza={confianza:.2f}, w={w}, h={h}", end="\r")

        except Exception as e:
            print(f"Error: {e}", end="\r")

    # Dibujar el último rectángulo detectado (entre análisis)
    if ultimo_rectangulo:
        x, y, w, h = ultimo_rectangulo
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Face Control - Test', frame)

    # waitKey(1) para máxima fluidez; 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()