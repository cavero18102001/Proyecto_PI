from django.shortcuts import render, redirect
from .models import Persona, Consulta, Mensaje
from .forms import PersonaForm

from .victorBot import victorBot

from gtts import gTTS
from playsound import playsound
from os import remove
import os
import os.path as path

from datetime import datetime
import random
from django.http import HttpResponse, JsonResponse
# Create your views here.
import re
import time
import pyttsx3 

# vistas basadas en funciones


# funcion para iniciar la aplicacion, para iniciar nuestro template
def reproducirAudio(respuesta):
    respuesta=re.sub("[<br>]","",respuesta)
    engine=pyttsx3.init()
    voices=engine.getProperty('voices')
    engine.setProperty ('rate', 120)
    engine.setProperty('voices',voices[1].id)
    engine.say(respuesta)
    engine.runAndWait()
    engine.stop()

def inicio(request):
    persona = Persona.objects.all()
    contexto = {"personas": persona}
    
    return render(request, 'chat.html', contexto)

# funcion para iniciar la aplicacion para iniciar nuestro template


def crearPersona(request):
    if request.method == 'GET':
        form = PersonaForm()
        contexto = {'form': form}
    else:
        form = PersonaForm(request.POST)
        contexto = {'form': form}
        print(form)
        if form.is_valid():
            form.save()
            return redirect('index')
    return render(request, 'crear_Persona.html', contexto)


def editarPersona(request, id):
    persona = Persona.objects.get(id=id)
    if request.method == 'GET':
        form = PersonaForm(instance=persona)
        contexto = {'form': form}
    else:
        form = PersonaForm(request.POST, instance=persona)
        contexto = {'form': form}
        if form.is_valid():
            form.save()
            return redirect('index')
    return render(request, 'crear_Persona.html', contexto)


def eliminarPersona(request, id):
    persona = Persona.objects.get(id=id)
    persona.delete()
    return redirect('index')


def message_view(request):
    return render(request, "messages.html",
                  {'users': "User.objects.exclude(username=request.user.username)",
                   'receiver': "User.objects.get(id=receiver)",
                   'messages': "hola"})


def inicio1(request):
    now = datetime.now()
    numeroAletorio = random.randint(1, 10000)
    tiempo = now.strftime("%m-%d-%Y,%H:%M:%S")
    idConsulta = str(numeroAletorio)+'-'+tiempo
    consulta = Consulta.objects.create(idConsulta=idConsulta)
    consulta.save()
    return redirect('consulta/'+idConsulta+'/')
    # redirect('/'+idConsulta+'/?usuario='+ciudadano)


def consulta(request, idConsulta):
    respuesta = ["Hola que tal!", "¿Cómo te va?", "un gusto de verte"]
    respuestaAletoria = random.choice(respuesta)
    usuario = "VICTOR"
    new_message = Mensaje.objects.create(
        mensaje=respuestaAletoria, usuario=usuario, idConsulta=idConsulta)
    new_message.save()

    reproducirAudio(respuestaAletoria)
    
    return render(request, 'messages.html', {
        'username': 'Ciudadano',
        'idConsulta': idConsulta,
    })


def getMessages(request, idConsulta):

    messages = Mensaje.objects.filter(idConsulta=idConsulta)
    return JsonResponse({"messages": list(messages.values())})


def send(request, idConsulta):

    message = request.POST['mensaje']
    usuario = "CIUDADANO"
    new_message = Mensaje.objects.create(
        mensaje=message, usuario=usuario, idConsulta=idConsulta)
    new_message.save()

    respuesta = victorBot(message)
    usuario = "VICTOR"
    new_message = Mensaje.objects.create(
        mensaje=respuesta, usuario=usuario, idConsulta=idConsulta)
    new_message.save()
    reproducirAudio(respuesta)
    return HttpResponse('Message sent successfully')
