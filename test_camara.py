import cv2

print("Versión de OpenCV:", cv2.__version__)

# Probar diferentes backends e índices
for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
    for index in [0, 1]:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Cámara funciona con backend={backend}, index={index}, shape={frame.shape}")
                cv2.imshow('Test', frame)
                cv2.waitKey(3000)
                cap.release()
                cv2.destroyAllWindows()
                exit()
            else:
                print(f"⚠️ Cámara abierta pero sin frame: backend={backend}, index={index}")
        cap.release()

print("❌ Ninguna combinación funcionó")