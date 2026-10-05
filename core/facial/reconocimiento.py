import numpy as np
from django.utils import timezone

from core.models import Alumno, RegistroAsistencia
from .registro import binario_a_encoding


def obtener_encodings_alumnos():
    alumnos = Alumno.objects.filter(
        activo=True,
        encoding_facial__isnull=False
    )

    encodings = []
    for alumno in alumnos:
        encoding = binario_a_encoding(alumno.encoding_facial)
        if encoding is not None:
            encodings.append((alumno, encoding))

    return encodings


def encontrar_alumno(encoding_actual, encodings_alumnos, umbral=0.4):
    if not encodings_alumnos:
        return None, None

    encoding_actual = np.array(encoding_actual, dtype=np.float32)
    norma_actual = np.linalg.norm(encoding_actual)
    if norma_actual > 0:
        encoding_actual = encoding_actual / norma_actual

    mejor_alumno = None
    mejor_distancia = float('inf')

    for alumno, encoding_guardado in encodings_alumnos:
        encoding_guardado = np.array(encoding_guardado, dtype=np.float32)
        norma_guardado = np.linalg.norm(encoding_guardado)
        if norma_guardado > 0:
            encoding_guardado = encoding_guardado / norma_guardado

        distancia = float(np.linalg.norm(encoding_actual - encoding_guardado))

        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_alumno = alumno

    if mejor_distancia <= umbral:
        return mejor_alumno, float(mejor_distancia)

    return None, float(mejor_distancia)


def obtener_horario_actual():
    """
    Devuelve el Horario que corresponde al día y hora actuales.
    Si hay varios, devuelve el primero.
    """
    from core.models import Horario

    ahora = timezone.localtime(timezone.now())
    dia_actual = ahora.weekday()  # 0=Lunes, 6=Domingo
    hora_actual = ahora.time()

    return Horario.objects.filter(
        dia_semana=dia_actual,
        hora_inicio__lte=hora_actual,
        hora_fin__gte=hora_actual
    ).select_related('grupo', 'materia', 'profesor').first()


def registrar_asistencia(alumno, horario=None, materia=None, profesor=None, confianza=None, metodo='FACIAL'):
    """
    Crea un RegistroAsistencia si el alumno no tiene uno hoy para ese horario.
    Devuelve (creado, registro).
    """
    hoy = timezone.now().date()

    # Verificar si ya tiene registro hoy para ese horario
    filtro = RegistroAsistencia.objects.filter(alumno=alumno, fecha=hoy)

    if horario:
        filtro = filtro.filter(horario=horario)
    else:
        filtro = filtro.filter(horario__isnull=True)

    if filtro.exists():
        return False, None

    # Determinar tipo según la hora límite del horario o del grupo
    tipo = 'ASISTENCIA'
    hora_limite = None

    if horario and horario.hora_limite_asistencia:
        hora_limite = horario.hora_limite_asistencia
    elif alumno.grupo and alumno.grupo.hora_limite_asistencia:
        hora_limite = alumno.grupo.hora_limite_asistencia

    if hora_limite:
        hora_actual = timezone.localtime(timezone.now()).time()
        if hora_actual > hora_limite:
            tipo = 'RETARDO'

    # Si se pasó un horario, usar su materia y profesor
    if horario:
        materia = horario.materia
        profesor = horario.profesor

    registro = RegistroAsistencia.objects.create(
        alumno=alumno,
        horario=horario,
        materia=materia,
        profesor=profesor,
        tipo=tipo,
        confianza=confianza,
        metodo=metodo,
    )

    return True, registro