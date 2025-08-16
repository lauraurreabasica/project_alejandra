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
    
class Insumo2(models.Model):
    imagen_url = models.CharField(max_length=500, blank=True, null=True)  # Guardará la URL de la imagen
    referencia = models.CharField(max_length=500, unique=True, null=True) 
    nombre = models.CharField(max_length=500, null=True) 
    medida = models.ForeignKey('Medida', on_delete=models.CASCADE)
    colores = models.ManyToManyField('Color')

    def __str__(self):
        return f"Insumo: {self.nombre}, Referencia: {self.referencia}"

class Producto(models.Model):
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    referencia = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100)
    colores = models.ManyToManyField(Color)

    # NUEVOS CAMPOS
    es_paquete = models.BooleanField(default=False)
    cantidad_por_paquete = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Producto: {self.nombre} (Ref: {self.referencia})"

class ProductoInsumo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo2, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, null=True, blank=True)  # 👈 NUEVO

    def __str__(self):
        return f"{self.producto.nombre} necesita {self.cantidad} de {self.insumo.nombre} ({self.color})"

class Proveedor(models.Model):
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'Número de Identificación Tributaria'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO, default='NIT')
    documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.documento}"


class Compra(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra {self.id} - {self.proveedor.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

class CompraInsumo(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, null=True, blank=True)
    produccion = models.ForeignKey('Produccion', on_delete=models.CASCADE, null=True, blank=True)
    insumo = models.ForeignKey('Insumo2', on_delete=models.CASCADE)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, default=1)  # Usar un ID válido
    cantidad = models.IntegerField()
    medida = models.ForeignKey('Medida', on_delete=models.CASCADE)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ESTADO_CHOICES = [
        ('Compra', 'Compra'),
        ('Reserva Producción', 'Reserva Producción'),
        ('Cancelado', 'Cancelado'),
        ('Terminado', 'Terminado'),
    ]
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='Compra')

    def total(self):
        return self.cantidad * self.valor_unitario

    def __str__(self):
        compra_str = f"Compra {self.compra.id}" if self.compra else (f"Producción {self.produccion.id}" if self.produccion else "Sin Origen")
        return f"{compra_str} - {self.insumo.nombre} ({self.cantidad} {self.medida.nombre}) - {self.color.nombre}"

class Cliente(models.Model):
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'Número de Identificación Tributaria'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO, default='CC')
    documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.documento}"

class Manualista(models.Model):
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'Número de Identificación Tributaria'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO, default='CC')
    documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)  # Campo opcional

    def __str__(self):
        return f"{self.nombre} - {self.documento}"

class EstadoProduccion(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    EN_PROCESO = 'En proceso', 'En proceso'
    TERMINADO = 'Terminado', 'Terminado'

class Produccion(models.Model):
    manualista = models.ForeignKey('Manualista', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_tentativa = models.DateField()
    estado = models.CharField(max_length=20, choices=EstadoProduccion.choices, default=EstadoProduccion.PENDIENTE)

    def __str__(self):
        return f"Producción {self.id} - {self.manualista.nombre} - {self.estado}"

class LineaProduccion(models.Model):
    produccion = models.ForeignKey(Produccion, on_delete=models.CASCADE, related_name='lineas')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    color = models.ForeignKey('Color', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produccion} - {self.producto.nombre} ({self.color.nombre}) x {self.cantidad}"

class EstadoProducto(models.TextChoices):
    EN_PRODUCCION = 'En producción', 'En producción'
    TERMINADO = 'Terminado', 'Terminado'
    VENDIDO = 'Vendido', 'Vendido'

class Venta(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

class InventarioProducto(models.Model):
    produccion = models.ForeignKey('Produccion', on_delete=models.CASCADE, null=True, blank=True)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    color = models.ForeignKey('Color', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=EstadoProducto.choices, default=EstadoProducto.EN_PRODUCCION)
    valor_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.produccion} {self.producto.nombre} ({self.color.nombre}) x {self.cantidad} - {self.estado}"
    

