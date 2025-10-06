from django.db import models

class DiaSemana(models.IntegerChoices):
    LUNES = 1, "Lunes"
    MARTES = 2, "Martes"
    MIERCOLES = 3, "Miércoles"
    JUEVES = 4, "Jueves"
    VIERNES = 5, "Viernes"
    SABADO = 6, "Sábado"
    DOMINGO = 7, "Domingo"
