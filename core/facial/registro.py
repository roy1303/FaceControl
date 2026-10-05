import os
import pickle
import numpy as np
from deepface import DeepFace


def extraer_encoding(ruta_foto):
    try:
        representaciones = DeepFace.represent(
            img_path=ruta_foto,
            model_name='Facenet',
            detector_backend='opencv',
            enforce_detection=True
        )

        if not representaciones:
            return None

        embedding = representaciones[0]['embedding']
        encoding = np.array(embedding, dtype=np.float32)

        # Normalizar a norma 1.0
        norma = np.linalg.norm(encoding)
        if norma > 0:
            encoding = encoding / norma

        return encoding

    except ValueError as e:
        print(f"No se detectó rostro: {e}")
        return None
    except Exception as e:
        print(f"Error al extraer encoding: {e}")
        return None


def encoding_a_binario(encoding):
    """
    Convierte un numpy array a bytes para guardarlo en BinaryField.
    """
    if encoding is None:
        return None
    return pickle.dumps(encoding)


def binario_a_encoding(binario):
    """
    Convierte bytes de vuelta a numpy array.
    """
    if binario is None:
        return None
    return pickle.loads(binario)


def registrar_alumno(alumno):
    """
    Extrae el encoding facial de la foto de un alumno y lo guarda.
    Devuelve True si tuvo éxito, False si no.
    """
    if not alumno.foto_referencia:
        print(f"El alumno {alumno} no tiene foto de referencia")
        return False

    ruta_foto = alumno.foto_referencia.path

    if not os.path.exists(ruta_foto):
        print(f"La foto no existe en: {ruta_foto}")
        return False

    print(f"Procesando foto de {alumno}...")
    encoding = extraer_encoding(ruta_foto)

    if encoding is None:
        print(f"No se pudo extraer el encoding de {alumno}")
        return False

    alumno.encoding_facial = encoding_a_binario(encoding)
    alumno.save()
    print(f"✅ Encoding guardado para {alumno}")
    return True