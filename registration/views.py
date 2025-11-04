from .forms import UserCreationFormWithEmail, EmailForm
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User, Group
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect 
from django import forms
from .models import Profile
from django.shortcuts import redirect, render
import secrets
import string
from django.core.paginator import Paginator
from django.db.models.query import QuerySet 
from .forms import CustomUserCreationForm, ProfileForm
from django.db.models import Q
from incidencia.models import Incidencia

class SignUpView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login') + '?register'
    
    def get_form(self, form_class=None):
        form = super(SignUpView,self).get_form()
        form.fields['username'].widget = forms.TextInput(attrs={'class':'form-control mb-2','placeholder':'Nombre de usuario'})
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        form.fields['password1'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Ingrese su contraseña'})
        form.fields['password2'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Re ingrese su contraseña'})    
        return form

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):

    success_url = reverse_lazy('profile')
    template_name = 'registration/profiles_form.html'

    def get_object(self):
        #recuperasmo el objeto a editar
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('check_group_main')
    template_name = 'registration/profile_email_form.html'

    def get_object(self):
        #recuperasmo el objeto a editar
        return self.request.user
    
    def get_form(self, form_class=None):
        form = super(EmailUpdate,self).get_form()
        #modificamos en tiempo real
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        return form
@login_required
def profile_edit(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        phone = request.POST.get('phone')
        User.objects.filter(pk=request.user.id).update(first_name=first_name)
        User.objects.filter(pk=request.user.id).update(last_name=last_name)
        Profile.objects.filter(user_id=request.user.id).update(phone=phone)
        Profile.objects.filter(user_id=request.user.id).update(mobile=mobile)
        messages.add_message(request, messages.INFO, 'Perfil Editado con éxito') 
    profile = Profile.objects.get(user_id = request.user.id)
    template_name = 'registration/profile_edit.html'
    return render(request,template_name,{'profile':profile})

'''Se creó la función main_Usuario dentro de registration porque no es necesario crear una app nueva (sólo en esta primera parte), ya que las tablas que 
utilizaremos para estas funciones ya existen en la app registration, por lo tanto no es necesario crear una app nueva.
Esta función está sacada del tercer tutorial del Canvas (CreandoApps). 
'''

@login_required
def main_usuario(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')

    if profile.group_id == 1:
        usuario_listado = User.objects.filter(is_active=True)
        usuario_listado = filtrar_usuarios_por_rol(request, usuario_listado)
        usuario_listado = usuario_listado.order_by('username')
        cantidad_activos=User.objects.filter(is_active=True).count()
        cantidad_incidencias=Incidencia.objects.count()
        paginator = Paginator(usuario_listado, 8) #para que funcione esta variable: from django.core.paginator import Paginator
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        todos_los_roles = Group.objects.all()
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        query_params = query_params.urlencode()
        return render(request, 'registration/main_usuario.html', {'page_obj': page_obj, 'todos_los_roles': todos_los_roles,'query_params': query_params, 'cantidad_activos':cantidad_activos,'cantidad_incidencias':cantidad_incidencias})
    else:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('logout')
    
def generar_password(longitud=10):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(caracteres) for i in range(longitud))

@login_required
def crear_usuario(request):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        if request.method == 'POST':
            user_form = CustomUserCreationForm(request.POST)
            profile_form = ProfileForm(request.POST)

            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.is_active = True
                user.save()
                user_profile = profile_form.save(commit=False)
                user_profile.user = user
                user_profile.save()
                user.groups.clear()
                user.groups.add(user_profile.group)

                messages.success(request, f'Usuario "{user.username}" creado correctamente.')
                return redirect('main_usuario')
        else:
            user_form = CustomUserCreationForm()
            profile_form = ProfileForm()

        return render(request, 'registration/crear_usuario.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    else:
        return redirect('logout')

@login_required
def ver_usuario(request, user_id):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')
    if profile.group_id == 1:
        try:
            usuario_count = User.objects.filter(pk=user_id).count()
            if usuario_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            usuario_data = User.objects.get(pk=user_id)
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'registration/ver_usuario.html'
        return render(request,template_name,{'usuario_data':usuario_data})
    else:
        return redirect('logout')

@login_required
def editar_usuario(request, user_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con el perfil.')
        return redirect('logout')

    if profile.group_id != 1:
        return redirect('logout')

    try:
        usuario_data = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('main_usuario')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        group_id = request.POST.get('group_id')
        if not all([username, first_name, last_name, email]):
            messages.warning(request, 'Todos los campos son obligatorios.')
            return redirect('editar_usuario', user_id=user_id)
        usuario_data.username = username
        usuario_data.first_name = first_name
        usuario_data.last_name = last_name
        usuario_data.email = email
        usuario_data.save()
        profile_usuario, created = Profile.objects.get_or_create(user=usuario_data)
        profile_usuario.telefono = telefono
        profile_usuario.save()
        if group_id:
            nuevo_grupo = Group.objects.get(id=group_id)
            usuario_data.groups.clear()
            usuario_data.groups.add(nuevo_grupo)

        messages.success(request, 'Datos del usuario actualizados correctamente.')
        return redirect('main_usuario')
    grupos = Group.objects.all()  
    template_name = 'registration/editar_usuario.html'
    context = {
        'usuario_data': usuario_data,
        'grupos': grupos
    }
    return render(request, template_name, context)
        
@login_required
def bloquear_desbloquear_usuario(request, user_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')
    if profile.group_id == 1:  #solo admins
        try:
            usuario = User.objects.get(pk=user_id)
            if usuario.is_superuser:
                messages.add_message(request, messages.WARNING, 'No está permitido bloquear cuentas de superusuario.')
                return redirect('main_usuario')
        
            usuario.is_active = not usuario.is_active
            usuario.save()
            if usuario.is_active:
                messages.add_message(request, messages.INFO, f'El usuario {usuario.username} fue DESBLOQUEADO con éxito.')
            else:
                messages.add_message(request, messages.INFO, f'El usuario {usuario.username} fue BLOQUEADO con éxito.')
            return redirect(request.META.get('HTTP_REFERER', 'main_usuario'))
        except User.DoesNoExist:
            messages.add_message(request, messages.INFO, 'El usuario no éxiste. ')
            return redirect('main_usuario')
    else:
        return redirect('logout')

@login_required
def main_usuario_bloqueados(request):
    try:
        profile=Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request,messages.INFO,'Hubo un error')
        return redirect('login')
    if profile.group_id == 1:
        usuario_bloqueado_listado=User.objects.filter(is_active=False).order_by('username')
        template_name = 'registration/main_usuario_bloqueados.html'
        return render(request, template_name, {'usuario_bloqueado_listado': usuario_bloqueado_listado})
    else:
        return redirect('logout')
    
@login_required
def profile_elimina(request, profile_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Hubo un error con el perfil')
        return redirect('logout')

    if profile.group_id == 1:
        profile_count = Profile.objects.filter(pk=profile_id).count()
        if profile_count <= 0:
            messages.add_message(request, messages.INFO, 'El perfil no existe')
            return redirect('check_profile')

        Profile.objects.filter(pk=profile_id).delete()
        messages.add_message(request, messages.INFO, 'Perfil eliminado')
        return redirect('main_profile')
    else:
        messages.add_message(request, messages.INFO, 'No autorizado')
        return redirect('logout')

def filtrar_usuarios_por_rol(request, usuarios: QuerySet) -> QuerySet:
    rol_id_filtro = request.GET.get('rol_id')
    if rol_id_filtro and rol_id_filtro.isdigit():
        return usuarios.filter(groups__id=rol_id_filtro)
    return usuarios

def ordenar_usuarios(request, usuarios: QuerySet) -> QuerySet:

    orden = request.GET.get('ordenar')
    if orden == 'alfabeticamente':
        return usuarios.order_by('username')
    return usuarios
'''
        lo siguiente sera comprobar que username, first_name, last_name, email estos argumentos existan como dato en algun registro de USER
        si existe se instancia, de lo contrario retorna error. 

        observacion: no se realmente si sera necesario editar el nombre y apellido de una persona ya que de manera muy excepcional las personas se cambian el nombre y apellido 
        

        try: 
            username_count = User.objects.filter(pk=user_id).count()
            if username_count <= 0:
                messages.add_message(request, messages.INFO, 'hubo un error')
                return redirect('check_profile')
            username_data = User.objects.get(pk=user_id)
        except:
            messages.add_message(request, messages.INFO, 'hubo un error')
            return redirect('check_profile')
        template_name = 'registrarion\editar_usuario.html'
        return render(request,template_name,{'username_data':username_data})
    else:
        return redirect('check_profile')
'''
