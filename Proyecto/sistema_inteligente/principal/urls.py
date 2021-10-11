from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio1, name='home'),
    path('consulta/<str:idConsulta>/', views.consulta, name='room'),
   # path('checkview', views.checkview, name='checkview'),
    path('enviar/<str:idConsulta>/', views.send, name='send'),
    path('getMessages/<str:idConsulta>/', views.getMessages, name='getMessages'),
]