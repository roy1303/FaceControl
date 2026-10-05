import json
import base64
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from deepface import DeepFace

from .facial.reconocimiento import (
    obtener_encodings_alumnos,
    encontrar_alumno,
    registrar_asistencia,
    obtener_horario_actual
)


class AsistenciaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket conectado")

    async def disconnect(self, close_code):
        print("WebSocket desconectado")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            frame_data = data.get('frame')
            horario_id = data.get('horario_id')

            if not frame_data:
                return

            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            resultado = await sync_to_async(self.procesar_frame)(frame, horario_id)
            await self.send(text_data=json.dumps(resultado))

        except Exception as e:
            print(f"Error en receive: {e}")
            await self.send(text_data=json.dumps({'status': 'error', 'mensaje': str(e)}))

    def procesar_frame(self, frame, horario_id=None):
        try:
            from .models import Horario

            # Obtener horario
            horario = None
            if horario_id:
                try:
                    horario = Horario.objects.filter(id=int(horario_id)).select_related(
                        'materia', 'profesor', 'grupo'
                    ).first()
                except (ValueError, TypeError):
                    horario = None
            else:
                # Detectar automáticamente el horario actual
                horario = obtener_horario_actual()

            encodings_alumnos = obtener_encodings_alumnos()

            if not encodings_alumnos:
                return {'status': 'no_alumnos'}

            representaciones = DeepFace.represent(
                img_path=frame,
                model_name='Facenet',
                detector_backend='opencv',
                enforce_detection=False,
                align=False
            )

            if not representaciones:
                return {'status': 'no_rostro'}

            rep = representaciones[0]
            encoding_actual = rep['embedding']

            alumno, distancia = encontrar_alumno(
                encoding_actual,
                encodings_alumnos,
                umbral=0.7
            )

            distancia_float = float(distancia) if distancia is not None else None

            if alumno:
                creado, registro = registrar_asistencia(
                    alumno,
                    horario=horario,
                    confianza=distancia_float
                )

                return {
                    'status': 'reconocido',
                    'nombre': f"{alumno.nombre} {alumno.apellido_paterno}",
                    'matricula': alumno.matricula,
                    'materia': horario.materia.nombre if horario else None,
                    'profesor': str(horario.profesor) if horario and horario.profesor else None,
                    'horario': str(horario) if horario else None,
                    'distancia': distancia_float,
                    'nuevo_registro': bool(creado),
                    'tipo': str(registro.tipo) if creado else None
                }
            else:
                return {
                    'status': 'desconocido',
                    'distancia': distancia_float
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'mensaje': str(e)}