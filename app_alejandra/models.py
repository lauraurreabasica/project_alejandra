from django.db import models

class Color(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Medida(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Referencia(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Nombre(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Insumo(models.Model):
    imagen_url = models.CharField(max_length=500, blank=True, null=True)  # Guardará la URL de la imagen
    referencia = models.ForeignKey('Referencia', on_delete=models.CASCADE)
    nombre = models.ForeignKey('Nombre', on_delete=models.CASCADE)
    medida = models.ForeignKey('Medida', on_delete=models.CASCADE)
    colores = models.ManyToManyField('Color')

    def __str__(self):
        return f"Insumo: {self.nombre.nombre}, Referencia: {self.referencia.nombre}"


