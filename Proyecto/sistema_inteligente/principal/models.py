from django.db import models
from datetime import datetime

# Create your models here.
class Persona(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=120)
    correo = models.EmailField(max_length=200)

    def __str__(self):
        return self.nombre

class Consulta(models.Model):
    idConsulta = models.CharField(max_length=100,primary_key=True)
    dia = models.DateTimeField(default=datetime.now, blank=True)
    estado = models.CharField(max_length=1,default="A")


class Mensaje(models.Model):
    idMensaje= models.AutoField(primary_key=True)
    mensaje = models.CharField(max_length=500)
    hora = models.DateTimeField(default=datetime.now, blank=True)
    usuario = models.CharField(max_length=10)
    estado = models.CharField(max_length=1,default="A")
    idConsulta = models.CharField(max_length=100)