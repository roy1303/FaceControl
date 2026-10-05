from django.contrib import admin
from .models import Grupo, Alumno, RegistroAsistencia, Materia, Profesor, Horario


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'numero_empleado', 'telefono')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'numero_empleado')
    filter_horizontal = ('materias',)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor', 'hora_limite_asistencia')
    search_fields = ('nombre',)
    list_filter = ('profesor',)
    filter_horizontal = ('materias',)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('get_dia_semana_display', 'hora_inicio', 'hora_fin', 'materia', 'grupo', 'profesor', 'aula')
    list_filter = ('dia_semana', 'grupo', 'materia', 'profesor')
    search_fields = ('grupo__nombre', 'materia__nombre', 'aula')
    ordering = ('dia_semana', 'hora_inicio')


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'apellido_paterno', 'apellido_materno', 'nombre', 'grupo', 'activo')
    search_fields = ('matricula', 'nombre', 'apellido_paterno', 'apellido_materno')
    list_filter = ('grupo', 'activo')
    list_editable = ('activo',)
    readonly_fields = ('fecha_registro',)


@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'materia', 'profesor', 'horario', 'fecha', 'hora', 'tipo', 'metodo', 'confianza')
    search_fields = ('alumno__nombre', 'alumno__apellido_paterno', 'alumno__matricula')
    list_filter = ('tipo', 'metodo', 'materia', 'profesor', 'fecha')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha', 'hora', 'fecha_hora')