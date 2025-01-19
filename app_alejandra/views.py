from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Color, Medida, Referencia, Nombre, Insumo

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
            referencia_id = request.POST.get('referencia')
            nombre_id = request.POST.get('nombre')
            medida_id = request.POST.get('medida')
            colores_ids = request.POST.getlist('colores')

            # Validar que los campos no estén vacíos
            if not (referencia_id and nombre_id and medida_id and colores_ids):
                messages.error(request, "Todos los campos deben estar completos.")
                return redirect('insumos')

            # Obtener las instancias relacionadas
            referencia = Referencia.objects.get(id=referencia_id)
            nombre = Nombre.objects.get(id=nombre_id)
            medida = Medida.objects.get(id=medida_id)
            colores = Color.objects.filter(id__in=colores_ids)

            # Crear un nuevo insumo y guardar "se guardo" en la columna imagen_url
            nuevo_insumo = Insumo.objects.create(
                imagen_url="se guardo",  # Valor fijo para la columna imagen_url
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
    return render(request, 'supplies.html', {
        'colores': colores,
        'medidas': medidas,
        'referencias': referencias,
        'nombres': nombres
    })
