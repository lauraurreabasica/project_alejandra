from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError
import json
from .models import Color, Medida, Referencia, Nombre, Insumo2,  Producto, ProductoInsumo, Proveedor, Compra, CompraInsumo
from .models import Cliente, Manualista, Produccion, LineaProduccion
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum, Max
import os
from django.conf import settings
from django.utils.text import slugify

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'login.html')

@login_required
def home_view(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def supplies_view(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "agregar_color":
            nuevo_color = request.POST.get('nuevo_color')
            if nuevo_color:
                if not Color.objects.filter(nombre__iexact=nuevo_color).exists():
                    Color.objects.create(nombre=nuevo_color)
                    messages.success(request, f"El color '{nuevo_color}' fue agregado correctamente.")
                else:
                    messages.error(request, f"El color '{nuevo_color}' ya existe.")
            return redirect('insumos')

        elif action == "agregar_medida":
            nueva_medida = request.POST.get('nueva_medida')
            if nueva_medida:
                if not Medida.objects.filter(nombre__iexact=nueva_medida).exists():
                    Medida.objects.create(nombre=nueva_medida)
                    messages.success(request, f"La medida '{nueva_medida}' fue agregada correctamente.")
                else:
                    messages.error(request, f"La medida '{nueva_medida}' ya existe.")
            return redirect('insumos')

        elif action == "agregar_nombre":
            nuevo_nombre = request.POST.get('nuevo_nombre')
            if nuevo_nombre:
                if not Nombre.objects.filter(nombre__iexact=nuevo_nombre).exists():
                    Nombre.objects.create(nombre=nuevo_nombre)
                    messages.success(request, f"El nombre '{nuevo_nombre}' fue agregada correctamente.")
                else:
                    messages.error(request, f"El nombre '{nuevo_nombre}' ya existe.")
            return redirect('insumos')

        elif action == "agregar_referencia":
            nueva_referencia = request.POST.get('nueva_referencia')
            if nueva_referencia:
                if not Referencia.objects.filter(nombre__iexact=nueva_referencia).exists():
                    Referencia.objects.create(nombre=nueva_referencia)
                    messages.success(request, f"La referencia '{nueva_referencia}' fue agregada correctamente.")
                else:
                    messages.error(request, f"La referencia '{nueva_referencia}' ya existe.")
            return redirect('insumos')

        elif action == "guardar_formulario":
            referencia = request.POST.get('nueva_referencia')
            nombre = request.POST.get('nuevo_nombre')
            medida_id = request.POST.get('medida')
            colores_ids = request.POST.getlist('colores')
            imagen_file = request.FILES.get('imagen')  # <<-- la imagen

            # Validar que los campos no estén vacíos
            if not (referencia and nombre and medida_id and colores_ids):
                messages.error(request, "Todos los campos deben estar completos.")
                return redirect('insumos')

            # Obtener las instancias relacionadas
            medida = Medida.objects.get(id=medida_id)
            colores = Color.objects.filter(id__in=colores_ids)

            # --- Guardar imagen en /imagenes con nombre insumo-<referencia>.<ext> ---
            imagen_rel_path = None
            try:
                # Carpeta /imagenes en la raíz del proyecto
                imagenes_root = os.path.join(settings.BASE_DIR, 'imagenes')
                os.makedirs(imagenes_root, exist_ok=True)

                if imagen_file:
                    # Extensión original (si no tiene, usamos .jpg)
                    _, ext = os.path.splitext(imagen_file.name)
                    ext = ext.lower() if ext else '.jpg'

                    # Nombre de archivo: insumo-<referencia-slug>.<ext>
                    base_name = f"insumo-{slugify(referencia)}"
                    filename = base_name + ext
                    dest_path = os.path.join(imagenes_root, filename)

                    # Si ya existe, versionamos: insumo-<ref>-1.ext, -2.ext, ...
                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base_name}-{counter}{ext}"
                        dest_path = os.path.join(imagenes_root, filename)
                        counter += 1

                    # Guardado en disco
                    with open(dest_path, 'wb+') as destination:
                        for chunk in imagen_file.chunks():
                            destination.write(chunk)

                    # Guardamos la ruta relativa para poder usarla en templates
                    imagen_rel_path = os.path.join('imagenes', filename)

            except Exception as e:
                messages.warning(request, f"No se pudo guardar la imagen: {str(e)}")

            # Crear Insumo2
            nuevo_insumo = Insumo2.objects.create(
                imagen_url=imagen_rel_path or "imagenes/placeholder.jpg",  # guarda la ruta (o un placeholder)
                referencia=referencia,
                nombre=nombre,
                medida=medida
            )
            nuevo_insumo.colores.set(colores)

            messages.success(request, "El formulario fue guardado exitosamente.")
            return redirect('insumos')

            
    # Obtener todos los datos para los dropdowns y checkboxes
    colores = Color.objects.all()
    medidas = Medida.objects.all()
    referencias = Referencia.objects.all()
    nombres = Nombre.objects.all()
    insumos_creados = Insumo2.objects.select_related('medida').prefetch_related('colores').all()

    return render(request, 'supplies.html', {
        'colores': colores,
        'medidas': medidas,
        'referencias': referencias,
        'nombres': nombres,
        'insumos_creados': insumos_creados 
    })

def product_view(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "guardar_formulario":
            referencia = request.POST.get('nueva_referencia')
            nombre = request.POST.get('nuevo_nombre')

            # Estos vienen de la tabla de insumos por fila
            insumos_ids = request.POST.getlist('insumo_id[]')
            cantidad_insumos = request.POST.getlist('cantidad[]')
            colores_insumo_ids = request.POST.getlist('color_id[]')

            # Imagen del producto
            imagen_file = request.FILES.get('imagen')

            # ✅ Paquetes
            es_paquete = request.POST.get('es_paquete') == 'on'
            cantidad_por_paquete = request.POST.get('cantidad_por_paquete')

            # Validación básica
            if not (referencia and nombre and insumos_ids and cantidad_insumos):
                messages.error(request, "Todos los campos obligatorios deben estar completos.")
                return redirect('productos')

            if es_paquete and not cantidad_por_paquete:
                messages.error(request, "Debes ingresar la cantidad por paquete.")
                return redirect('productos')

            # --- Guardar imagen en /imagenes con nombre producto-<referencia>.<ext> ---
            imagen_rel_path = None
            try:
                imagenes_root = os.path.join(settings.BASE_DIR, 'imagenes')
                os.makedirs(imagenes_root, exist_ok=True)

                if imagen_file:
                    _, ext = os.path.splitext(imagen_file.name)
                    ext = ext.lower() if ext else '.jpg'

                    base_name = f"producto-{slugify(referencia)}"
                    filename = base_name + ext
                    dest_path = os.path.join(imagenes_root, filename)

                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base_name}-{counter}{ext}"
                        dest_path = os.path.join(imagenes_root, filename)
                        counter += 1

                    with open(dest_path, 'wb+') as destination:
                        for chunk in imagen_file.chunks():
                            destination.write(chunk)

                    imagen_rel_path = os.path.join('imagenes', filename)
            except Exception as e:
                messages.warning(request, f"No se pudo guardar la imagen del producto: {str(e)}")

            try:
                # Crear o actualizar el producto por referencia
                nuevo_producto, creado = Producto.objects.get_or_create(
                    referencia=referencia,
                    defaults={
                        'nombre': nombre,
                        'imagen': imagen_rel_path or "imagenes/placeholder.jpg",
                        'es_paquete': es_paquete,
                        'cantidad_por_paquete': int(cantidad_por_paquete) if es_paquete else None
                    }
                )

                if not creado:
                    # Actualiza datos si ya existía
                    nuevo_producto.nombre = nombre
                    nuevo_producto.es_paquete = es_paquete
                    nuevo_producto.cantidad_por_paquete = int(cantidad_por_paquete) if es_paquete else None
                    if imagen_rel_path:  # solo si subieron una nueva imagen
                        nuevo_producto.imagen = imagen_rel_path
                    nuevo_producto.save()

                # Guarda líneas de insumos del producto
                if not creado:
                    ProductoInsumo.objects.filter(producto=nuevo_producto).delete()

                for insumo_id, cantidad, color_id in zip(insumos_ids, cantidad_insumos, colores_insumo_ids):
                    if not insumo_id or not cantidad:
                        continue
                    insumo = Insumo2.objects.get(id=insumo_id)
                    color = Color.objects.get(id=color_id) if color_id else None
                    ProductoInsumo.objects.create(
                        producto=nuevo_producto,
                        insumo=insumo,
                        cantidad=int(cantidad),
                        color=color
                    )

                messages.success(request, "El producto y sus insumos fueron guardados correctamente.")
                return redirect('productos')

            except IntegrityError:
                messages.error(request, "Error al guardar el producto. Verifica los datos.")
                return redirect('productos')

            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")
                return redirect('productos')


    # Datos para renderizar el formulario
    colores = Color.objects.all()
    medidas = Medida.objects.all()
    referencias = Referencia.objects.all()
    nombres = Nombre.objects.all()
    insumos_data = Insumo2.objects.all()
    insumos = [{'id': i.id, 'nombre': i.nombre} for i in insumos_data]
    colores2 = {
        insumo.id: list(insumo.colores.values('id', 'nombre')) for insumo in Insumo2.objects.prefetch_related('colores')
    }

    productos_creados = Producto.objects.prefetch_related('colores').all()

    return render(request, 'productos.html', {
        'colores_json': json.dumps(colores2), 
        'colores': colores,
        'medidas': medidas,
        'referencias': referencias,
        'nombres': nombres,
        'insumos': insumos,
        'productos_creados': productos_creados  # 👈 Nuevo
    })



def proveedor_view(request):
    if request.method == "POST":
        tipo_documento = request.POST.get('tipo_documento')
        documento = request.POST.get('documento')
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')

        # Verificar que los campos no estén vacíos
        if nombre and documento and tipo_documento:
            # Verificar si el proveedor ya existe por su documento
            if not Proveedor.objects.filter(documento=documento).exists():
                Proveedor.objects.create(
                    tipo_documento=tipo_documento,
                    documento=documento,
                    nombre=nombre,
                    telefono=telefono,
                    email=email,
                    direccion=direccion
                )
                messages.success(request, f"El proveedor '{nombre}' fue agregado correctamente.")
            else:
                messages.warning(request, f"El proveedor con documento '{documento}' ya existe.")
        else:
            messages.error(request, "El tipo de documento, documento y nombre son obligatorios.")

        return redirect('proveedores')

    # Obtener todos los proveedores de la base de datos
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores.html', {'proveedores': proveedores})

def eliminar_proveedor(request, proveedor_id):
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        proveedor.delete()
        messages.success(request, f"El proveedor '{proveedor.nombre}' ha sido eliminado.")
    except Proveedor.DoesNotExist:
        messages.error(request, "El proveedor no existe.")
    
    return redirect('proveedores')

def compras_view(request):
    if request.method == "POST":
        proveedor_id = request.POST.get('proveedor')
        insumos_ids = request.POST.getlist('insumo_id[]')
        colores_ids = request.POST.getlist('color_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        valores = request.POST.getlist('valor_unitario[]')

        # Validación
        if not proveedor_id or not insumos_ids or not cantidades or not valores or not colores_ids:
            messages.error(request, "Debe seleccionar un proveedor, insumos y valores correctos.")
            return redirect('compras')

        proveedor = Proveedor.objects.get(id=proveedor_id)
        nueva_compra = Compra.objects.create(proveedor=proveedor)

        for insumo_id, color_id, cantidad, valor in zip(insumos_ids, colores_ids, cantidades, valores):
            insumo = Insumo2.objects.get(id=insumo_id)
            color = Color.objects.get(id=color_id)
            medida = insumo.medida
            CompraInsumo.objects.create(
                compra=nueva_compra,
                insumo=insumo,
                color=color,
                cantidad=int(cantidad),
                medida=medida,
                valor_unitario=float(valor)
            )

        messages.success(request, "Compra registrada exitosamente.")
        return redirect('compras')

    proveedores = Proveedor.objects.all()
    insumos = list(Insumo2.objects.values('id', 'nombre', 'medida_id'))
    medidas = {medida.id: medida.nombre for medida in Medida.objects.all()}
    colores = {insumo.id: list(insumo.colores.values('id', 'nombre')) for insumo in Insumo2.objects.prefetch_related('colores')}

    precios_anteriores = {}

    for proveedor in proveedores:
        for insumo in insumos:
            ultima = CompraInsumo.objects.filter(
                compra__proveedor=proveedor,
                insumo_id=insumo["id"]
            ).order_by('-compra__fecha').first()
            if ultima:
                key = f"{proveedor.id}_{insumo['id']}"
                precios_anteriores[key] = float(ultima.valor_unitario)

    

    return render(request, 'compras.html', {
        'proveedores': proveedores,
        'insumos_json': json.dumps(insumos),
        'medidas_json': json.dumps(medidas),
        'colores_json': json.dumps(colores),
        'precios_anteriores': json.dumps(precios_anteriores),
    })

def cliente_view(request):
    if request.method == "POST":
        tipo_documento = request.POST.get('tipo_documento')
        documento = request.POST.get('documento')
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')

        # Verificar que los campos no estén vacíos
        if nombre and documento and tipo_documento:
            # Verificar si el cliente ya existe por su documento
            if not Cliente.objects.filter(documento=documento).exists():
                Cliente.objects.create(
                    tipo_documento=tipo_documento,
                    documento=documento,
                    nombre=nombre,
                    telefono=telefono,
                    email=email,
                    direccion=direccion
                )
                messages.success(request, f"El cliente '{nombre}' fue agregado correctamente.")
            else:
                messages.warning(request, f"El cliente con documento '{documento}' ya existe.")
        else:
            messages.error(request, "El tipo de documento, documento y nombre son obligatorios.")

        return redirect('clientes')

    # Obtener todos los clientes de la base de datos
    clientes = Cliente.objects.all()
    return render(request, 'clientes.html', {'clientes': clientes})

def eliminar_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        cliente.delete()
        messages.success(request, f"El cliente '{cliente.nombre}' ha sido eliminado.")
    except Cliente.DoesNotExist:
        messages.error(request, "El cliente no existe.")
    
    return redirect('clientes')

def manualista_view(request):
    if request.method == "POST":
        tipo_documento = request.POST.get('tipo_documento')
        documento = request.POST.get('documento')
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # Si el usuario no quiere guardar la fecha, se deja como None
        if fecha_nacimiento == "":
            fecha_nacimiento = None
        else:
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Formato de fecha inválido.")
                return redirect('manualistas')

        if nombre and documento and tipo_documento:
            if not Manualista.objects.filter(documento=documento).exists():
                Manualista.objects.create(
                    tipo_documento=tipo_documento,
                    documento=documento,
                    nombre=nombre,
                    telefono=telefono,
                    email=email,
                    direccion=direccion,
                    fecha_nacimiento=fecha_nacimiento
                )
                messages.success(request, f"La manualista '{nombre}' fue agregada correctamente.")
            else:
                messages.warning(request, f"La manualista con documento '{documento}' ya existe.")
        else:
            messages.error(request, "El tipo de documento, documento y nombre son obligatorios.")

        return redirect('manualistas')

    manualistas = Manualista.objects.all()
    return render(request, 'manualistas.html', {'manualistas': manualistas})


def eliminar_manualista(request, manualista_id):
    try:
        manualista = Manualista.objects.get(id=manualista_id)
        manualista.delete()
        messages.success(request, f"La manualista '{manualista.nombre}' ha sido eliminada.")
    except Manualista.DoesNotExist:
        messages.error(request, "La manualista no existe.")
    
    return redirect('manualistas')

def produccion_view(request):
    if request.method == "POST":
        manualista_id = request.POST.get('manualista')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_tentativa = request.POST.get('fecha_tentativa')
        productos_ids = request.POST.getlist('producto_id[]')
        colores_ids = request.POST.getlist('color_id[]')
        cantidades = request.POST.getlist('cantidad[]')

        # Validaciones
        if not (manualista_id and fecha_inicio and fecha_tentativa and productos_ids and colores_ids and cantidades):
            messages.error(request, "Todos los campos deben estar completos.")
            return redirect('produccion')

        manualista = Manualista.objects.get(id=manualista_id)
        nueva_produccion = Produccion.objects.create(
            manualista=manualista,
            fecha_inicio=fecha_inicio,
            fecha_tentativa=fecha_tentativa,
            estado="Pendiente"
        )

        insumos_a_reservar = []  # Lista temporal para guardar insumos a reservar

        for producto_id, color_id, cantidad in zip(productos_ids, colores_ids, cantidades):
            producto = Producto.objects.get(id=producto_id)
            color = Color.objects.get(id=color_id)
            cantidad = int(cantidad)

            # Guardar el producto en la orden de producción
            LineaProduccion.objects.create(
                produccion=nueva_produccion,
                producto=producto,
                color=color,
                cantidad=cantidad
            )

            # Obtener los insumos requeridos para el producto
            insumos = ProductoInsumo.objects.filter(producto=producto)

            for insumo in insumos:
                # Determinar si el insumo tiene el color correcto o si se usa "SinColor"
                insumo_color = color if insumo.insumo.colores.filter(id=color.id).exists() else Color.objects.get(nombre="SinColor")
                insumo_total = cantidad * insumo.cantidad  # Multiplicar cantidad de insumo por cantidad de productos

                # Verificar existencias disponibles
                compras_total = CompraInsumo.objects.filter(
                    insumo=insumo.insumo,
                    color=insumo_color
                ).aggregate(total=Sum('cantidad'))['total'] or 0

                if compras_total < insumo_total:
                    messages.error(request, f"No hay suficiente stock de {insumo.insumo.nombre} ({insumo_color.nombre}). Producción cancelada.")
                    nueva_produccion.delete()  # Eliminar la producción si no hay suficiente stock
                    return redirect('produccion')

                # Agregar a la lista de insumos reservados
                insumos_a_reservar.append({
                    'insumo': insumo.insumo,
                    'color': insumo_color,
                    'cantidad': insumo_total
                })

        # Registrar los insumos reservados en `CompraInsumo`
        for reserva in insumos_a_reservar:
            CompraInsumo.objects.create(
                insumo=reserva['insumo'],
                color=reserva['color'],
                cantidad=-reserva['cantidad'],  # Se registra como negativo para indicar reserva
                compra=None  # Indica que no es una compra sino una reserva por producción
            )

        messages.success(request, "Orden de producción creada exitosamente con insumos reservados.")
        return redirect('produccion')

    manualistas = Manualista.objects.all()
    productos = list(Producto.objects.values('id', 'nombre'))
    colores = {producto['id']: list(Color.objects.filter(producto__id=producto['id']).values('id', 'nombre')) for producto in productos}

    return render(request, 'produccion.html', {
        'manualistas': manualistas,
        'productos_json': json.dumps(productos),
        'colores_json': json.dumps(colores),
    })

def calcular_produccion(request):
    productos_ids = request.GET.getlist('producto_id[]')
    # colores_ids = request.GET.getlist('color_id[]')
    cantidades = request.GET.getlist('cantidad[]')

    # Corregir el problema de los valores concatenados en un solo string
    if len(productos_ids) == 1 and "," in productos_ids[0]:
        productos_ids = productos_ids[0].split(",")

    # if len(colores_ids) == 1 and "," in colores_ids[0]:
    #     colores_ids = colores_ids[0].split(",")

    if len(cantidades) == 1 and "," in cantidades[0]:
        cantidades = cantidades[0].split(",")

    errores = []
    insumos_requeridos = {}

    for producto_id, cantidad in zip(productos_ids, cantidades):
        if not producto_id or not cantidad:  
            continue  

        cantidad = int(cantidad)
        producto = Producto.objects.get(id=producto_id)
        insumos = ProductoInsumo.objects.filter(producto=producto)

        for insumo in insumos:
            insumo_color_valido = True
            # colores_insumo = insumo.insumo.colores.all()

            # Si el insumo tiene "SinColor", se permite cualquier color
            # if colores_insumo.filter(nombre="SinColor").exists():
            #     insumo_color_valido = True
            # elif colores_insumo.filter(id=color.id).exists():
            #     insumo_color_valido = True
            # else:
            #     errores.append(f"El insumo '{insumo.insumo.nombre}' no tiene el color '{color.nombre}'.")

            if insumo_color_valido:
                insumo_total = cantidad * insumo.cantidad  
                insumo_id = insumo.insumo.id
                insumo_color = insumo.color.nombre
                color = insumo.color.id
                insumo_medida = insumo.insumo.medida.nombre if insumo.insumo.medida else "N/A"

                # Obtener la cantidad disponible en `CompraInsumo`
                compras_total = CompraInsumo.objects.filter(
                    insumo=insumo.insumo,
                    color=color
                ).aggregate(total=Sum('cantidad'))['total'] or 0

                

                # Calcular faltantes
                cantidad_disponible = compras_total 
                faltantes = insumo_total - cantidad_disponible if insumo_total > cantidad_disponible else 0

                if f'{insumo_id}-{color}' in insumos_requeridos:
                    insumos_requeridos[f'{insumo_id}-{color}']['cantidad'] += insumo_total
                    insumos_requeridos[f'{insumo_id}-{color}']['faltantes'] += faltantes
                else:
                    insumos_requeridos[f'{insumo_id}-{color}'] = {
                        'nombre': insumo.insumo.nombre,
                        'cantidad': insumo_total,
                        'color': insumo_color,
                        'medida': insumo_medida,
                        'faltantes': faltantes
                    }
    for key in insumos_requeridos.keys():
        ids = key.split('-')
        # Obtener la cantidad disponible en `CompraInsumo`
        compras_total = CompraInsumo.objects.filter(
            insumo=ids[0],
            color=ids[1]
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        insumos_requeridos[key]['faltantes'] = insumos_requeridos[key]['cantidad'] - compras_total
        pass

    return JsonResponse({'errores': errores, 'insumos_requeridos': list(insumos_requeridos.values())})