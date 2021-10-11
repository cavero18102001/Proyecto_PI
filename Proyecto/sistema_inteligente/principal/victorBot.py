# es un conjunto de bibliotecas y programas para el procesamiento del lenguaje natural simbólico y estadísticos
# para el lenguaje de programación Python.
import json
# guardar nuestro modelo para no cargar de nuevo el bot
import pickle
# escojer una respuesta aletoria
import random
from tensorflow.python.framework import ops
import tflearn
import numpy
# Procesamiento del lenguaje natural
import nltk
# Quitar algunas letras para que el chatbot entienda mejor
from nltk.stem.lancaster import LancasterStemmer
# libreria de reconocimienro de voz
import speech_recognition as sr

import os

# nltk.download('punkt')
# creamos un objeto de la clase
stemmer = LancasterStemmer()
# creamos un objeto recognizer
recognizer = sr.Recognizer()

# # cargar un modelo de datos para no estar haciendo bucles ala hora que se ejecute el programa


# el archivo .json tendra nuestras posibles respuestas

def funcionEntrenamiento(palabras, tags, auxX, auxY):
    try:
        with open(os.path.join(os.path.dirname(__file__),"/datos/variables.pickle", 'rb')) as archivoPickle:
            palabras, tags, entrenamiento, salida = pickle.load(archivoPickle)
    except:
        with open(os.path.join(os.path.dirname(__file__), 'datos/contenido.json'), encoding='utf-8') as archivo:
            datos = json.load(archivo)
        for contenido in datos["contenido"]:
            for patrones in contenido["patrones"]:
                # reconoce puntos especiales, separa las palabras de una cadena
                auxPalabra = nltk.word_tokenize(patrones)
                palabras.extend(auxPalabra)
                # agrega al final de la lista
                auxX.append(auxPalabra)
                auxY.append(contenido["tag"])
                if contenido["tag"] not in tags:
                    tags.append(contenido["tag"])
        # WordNet es una base de datos léxica del Idioma inglés​ que agrupa palabras en inglés en conjuntos de sinónimos
        #  llamados synsets, proporcionando definiciones cortas y generales y almacenando las relaciones semánticas entre los
        #  conjuntos de sinónimos

        # el metodo .stem recibe como parametro el metodo .lower que convierte a minusculas
        # recore todas las palabras y si es que encuentra un simbolo ? no lo toma en cuenta
        palabras = [stemmer.stem(w.lower()) for w in palabras if w != "?"]
        # sorted regresa una lista de algo ya ordenado
        palabras = sorted(list(set(palabras)))
        tags = sorted(tags)

        # algoritmo de la cubeta: si esta una palabra dentro de una conjunto de palabras
        entrenamiento = []
        salida = []
        # salida vacia que esta llena de ceros
        salidaVacia = [0 for _ in range(len(tags))]
        # en x se guardara el indice y en documento la palabra
        for x, documento in enumerate(auxX):
            cubeta = []
            auxPalabra = [stemmer.stem(w.lower()) for w in documento]
            for w in palabras:
                if w in auxPalabra:
                    cubeta.append(1)
                else:
                    cubeta.append(0)
            filaSalida = salidaVacia[:]
            filaSalida[tags.index(auxY[x])] = 1
            entrenamiento.append(cubeta)
            salida.append(filaSalida)

            with open(os.path.join(os.path.dirname(__file__), 'datos/variables.pickle'), 'wb') as archivoPickle:
                pickle.dump(
                    (palabras, tags, entrenamiento, salida), archivoPickle)
    return palabras, tags, entrenamiento, salida


# crear la red neuronal

def crearRedNeuronal(entrenamiento, salida):
    # convertir la lista entrenamiento en areglos numpy
    entrenamiento = numpy.array(entrenamiento)
    # convertir la lista salida en areglos numpy
    salida = numpy.array(salida)
    # colocar la red neuronal en blanco o reiniciar
    ops.reset_default_graph()
    # creamos la red neuronal
    # de parametros recibe: ninguna forma, la longitud del entrenamiento
    red = tflearn.input_data(shape=[None, len(entrenamiento[0])])
    # Le pasamos la red y 10 neuronas
    # tenemos dos columnas de neuronas que haran todo el trabajo
    red = tflearn.fully_connected(red, 10)
    red = tflearn.fully_connected(red, 10)

    red = tflearn.fully_connected(red, len(salida[0]), activation='softmax')
    # verificar errores
    red = tflearn.regression(red)
    return red, entrenamiento, salida

def cargarModelo(modelo, entrenamiento, salida):
    try:
        modelo.load(os.path.join(os.path.dirname(__file__), 'datos/modelo.tflearn'))
    except:
        # llenamos el modelo
        # parametros: entrenamiento,salida, va ver 1000 veces que nuestro lo vea,
        # la cantidad de patrones segun archivo contenido,
        modelo.fit(entrenamiento, salida, n_epoch=2000,
                batch_size=1500, show_metric=True)
        modelo.save(os.path.join(os.path.dirname(__file__), 'datos/modelo.tflearn'))


def victorBot(msg):
    palabras, tags, entrenamiento, salida = funcionEntrenamiento(palabras = [], tags = [], auxX = [], auxY = [])
    red,entrenamiento, salida=crearRedNeuronal(entrenamiento, salida)
    
    # creamos el modelo
    modelo = tflearn.DNN(red)
    cargarModelo(modelo, entrenamiento, salida)
    with open(os.path.join(os.path.dirname(__file__), 'datos/contenido.json'), encoding='utf-8') as archivo:
        datos = json.load(archivo)
        while True:
            entrada = msg
            cubeta = [0 for _ in range(len(palabras))]
            entradaProcesada = nltk.word_tokenize(entrada)
            entradaProcesada = [stemmer.stem(w.lower())
                                for w in entradaProcesada]
            for palabraIndividual in entradaProcesada:
                for i, palabra in enumerate(palabras):
                    if palabra == palabraIndividual:
                        cubeta[i] = 1
            resultados = modelo.predict([numpy.array(cubeta)])
            resultadosIndices = numpy.argmax(resultados)
            tag = tags[resultadosIndices]
            for tagAux in datos["contenido"]:
                if tagAux['tag'] == tag:
                    respuesta = tagAux["respuestas"]
            return random.choice(respuesta)
