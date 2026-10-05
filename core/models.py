from django.db import models
from django.contrib.auth.models import User


class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ['nombre']


class Profesor(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profesor'
    )
    numero_empleado = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    materias = models.ManyToManyField(
        Materia,
        related_name='profesores',
        blank=True
    )

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f"{nombre} ({self.numero_empleado})"

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"


class Grupo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    profesor = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='grupos'
    )
    materias = models.ManyToManyField(
        Materia,
        related_name='grupos',
        blank=True
    )
    hora_limite_asistencia = models.TimeField(
        help_text="Hora a partir de la cual se considera retardo"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"


class Horario(models.Model):
    DIA_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE,
        related_name='horarios'
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE,
        related_name='horarios'
    )
    profesor = models.ForeignKey(
        Profesor, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='horarios'
    )
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    hora_limite_asistencia = models.TimeField(
        help_text="Hora a partir de la cual se considera retardo en esta clase"
    )
    aula = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} | {self.materia} ({self.grupo})"

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ('grupo', 'materia', 'dia_semana', 'hora_inicio')


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    matricula = models.CharField(max_length=20, unique=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True)
    foto_referencia = models.ImageField(upload_to='alumnos/fotos/', blank=True, null=True)
    encoding_facial = models.BinaryField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombre} ({self.matricula})"

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']


class RegistroAsistencia(models.Model):
    TIPO_CHOICES = [
        ('ASISTENCIA', 'Asistencia'),
        ('RETARDO', 'Retardo'),
        ('FALTA', 'Falta'),
    ]

    METODO_CHOICES = [
        ('FACIAL', 'Reconocimiento Facial'),
        ('MANUAL', 'Manual'),
        ('QR', 'Código QR'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='asistencias')
    materia = models.ForeignKey(
        Materia, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros'
    )
    profesor = models.ForeignKey(
        Profesor, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros'
    )
    horario = models.ForeignKey(
        Horario, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros'
    )
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='ASISTENCIA')
    confianza = models.FloatField(null=True, blank=True)
    metodo = models.CharField(max_length=10, choices=METODO_CHOICES, default='FACIAL')
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_tomados'
    )

    def __str__(self):
        return f"{self.alumno} - {self.fecha} {self.hora} ({self.tipo})"

    class Meta:
        verbose_name = "Registro de Asistencia"
        verbose_name_plural = "Registros de Asistencia"
        ordering = ['-fecha_hora']
        unique_together = ('alumno', 'fecha', 'horario')