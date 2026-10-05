import os
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone

from .models import Alumno, Grupo, RegistroAsistencia, Materia, Profesor, Horario
from .facial.exportar import exportar_asistencias_a_excel
from .facial.reconocimiento import obtener_horario_actual


def inicio(request):
    total_alumnos = Alumno.objects.filter(activo=True).count()
    total_grupos = Grupo.objects.count()
    total_registros_hoy = RegistroAsistencia.objects.filter(
        fecha=datetime.now().date()
    ).count()

    context = {
        'total_alumnos': total_alumnos,
        'total_grupos': total_grupos,
        'total_registros_hoy': total_registros_hoy,
    }
    return render(request, 'core/inicio.html', context)


def lista_alumnos(request):
    alumnos = Alumno.objects.filter(activo=True).select_related('grupo')

    grupo_id = request.GET.get('grupo')
    if grupo_id:
        alumnos = alumnos.filter(grupo_id=grupo_id)

    busqueda = request.GET.get('q')
    if busqueda:
        alumnos = alumnos.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido_paterno__icontains=busqueda) |
            Q(apellido_materno__icontains=busqueda) |
            Q(matricula__icontains=busqueda)
        )

    grupos = Grupo.objects.all()

    context = {
        'alumnos': alumnos,
        'grupos': grupos,
        'grupo_seleccionado': grupo_id,
        'busqueda': busqueda or '',
    }
    return render(request, 'core/lista_alumnos.html', context)


def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    asistencias = RegistroAsistencia.objects.filter(
        alumno=alumno
    ).select_related('materia', 'profesor', 'horario').order_by('-fecha_hora')[:30]

    context = {
        'alumno': alumno,
        'asistencias': asistencias,
    }
    return render(request, 'core/detalle_alumno.html', context)


def bitacora(request):
    registros = RegistroAsistencia.objects.all().select_related(
        'alumno', 'alumno__grupo', 'materia', 'profesor', 'horario'
    )

    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    grupo_id = request.GET.get('grupo')
    tipo = request.GET.get('tipo')
    materia_id = request.GET.get('materia')
    profesor_id = request.GET.get('profesor')
    horario_id = request.GET.get('horario')

    if fecha_desde:
        registros = registros.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha__lte=fecha_hasta)
    if grupo_id:
        registros = registros.filter(alumno__grupo_id=grupo_id)
    if tipo:
        registros = registros.filter(tipo=tipo)
    if materia_id:
        registros = registros.filter(materia_id=materia_id)
    if profesor_id:
        registros = registros.filter(profesor_id=profesor_id)
    if horario_id:
        registros = registros.filter(horario_id=horario_id)

    context = {
        'registros': registros[:200],
        'grupos': Grupo.objects.all(),
        'materias': Materia.objects.all(),
        'profesores': Profesor.objects.all(),
        'horarios': Horario.objects.all().select_related('grupo', 'materia'),
        'fecha_desde': fecha_desde or '',
        'fecha_hasta': fecha_hasta or '',
        'grupo_seleccionado': grupo_id or '',
        'tipo_seleccionado': tipo or '',
        'materia_seleccionada': materia_id or '',
        'profesor_seleccionado': profesor_id or '',
        'horario_seleccionado': horario_id or '',
    }
    return render(request, 'core/bitacora.html', context)


def descargar_excel(request):
    registros = RegistroAsistencia.objects.all().select_related(
        'alumno', 'alumno__grupo', 'materia', 'profesor', 'horario'
    )

    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    grupo_id = request.GET.get('grupo')
    tipo = request.GET.get('tipo')
    materia_id = request.GET.get('materia')
    profesor_id = request.GET.get('profesor')
    horario_id = request.GET.get('horario')

    if fecha_desde:
        registros = registros.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha__lte=fecha_hasta)
    if grupo_id:
        registros = registros.filter(alumno__grupo_id=grupo_id)
    if tipo:
        registros = registros.filter(tipo=tipo)
    if materia_id:
        registros = registros.filter(materia_id=materia_id)
    if profesor_id:
        registros = registros.filter(profesor_id=profesor_id)
    if horario_id:
        registros = registros.filter(horario_id=horario_id)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f'bitacora_face_control_{timestamp}.xlsx'
    ruta_temporal = os.path.join('media', nombre_archivo)

    os.makedirs('media', exist_ok=True)
    exportar_asistencias_a_excel(registros, ruta_salida=ruta_temporal)

    with open(ruta_temporal, 'rb') as f:
        response = HttpResponse(
            f.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    os.remove(ruta_temporal)
    return response


def tomar_asistencia(request):
    horario_actual = obtener_horario_actual()

    context = {
        'horarios': Horario.objects.all().select_related('grupo', 'materia', 'profesor'),
        'horario_actual': horario_actual,
    }
    return render(request, 'core/tomar_asistencia.html', context)