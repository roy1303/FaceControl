from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('alumnos/', views.lista_alumnos, name='lista_alumnos'),
    path('alumnos/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),
    path('bitacora/', views.bitacora, name='bitacora'),
    path('bitacora/excel/', views.descargar_excel, name='descargar_excel'),
    path('asistencia/', views.tomar_asistencia, name='tomar_asistencia'),
]