import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator
from .models import Arena, Jogo
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import re
import cloudinary
import cloudinary.uploader
import os
from django.conf import settings

class ArenaForm(forms.ModelForm):
    class Meta:
        model = Arena
        fields = ['nome', 'logradouro', 'bairro', 'cidade', 'estado',
                 'cep', 'latitude', 'longitude', 'foto_quadra']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Construir o endereço completo
        endereco_parts = []
        if self.cleaned_data.get('logradouro'): 
            endereco_parts.append(self.cleaned_data['logradouro'])
        if self.cleaned_data.get('bairro'):
            endereco_parts.append(self.cleaned_data['bairro'])
        if self.cleaned_data.get('cidade'):
            endereco_parts.append(self.cleaned_data['cidade'])
        if self.cleaned_data.get('estado'):
            endereco_parts.append(self.cleaned_data['estado'])
        if self.cleaned_data.get('cep'):
            endereco_parts.append(self.cleaned_data['cep'])
        
        # Atualizar o campo endereço
        instance.endereco = ', '.join(filter(None, endereco_parts))
        
        # Tratar o upload da foto da quadra para o Cloudinary
        if self.cleaned_data.get('foto_quadra'):
            try:
                # Configurar Cloudinary explicitamente
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )
                
                # Processar a imagem
                image = Image.open(self.cleaned_data['foto_quadra'])
                image = self._process_image(image)
                
                # Preparar para salvar
                image_io = BytesIO()
                image.save(image_io, format='JPEG', quality=90)
                image_io.seek(0)
                
                # Gerar nome de arquivo único
                file_name = self.cleaned_data['foto_quadra'].name
                base_name, ext = os.path.splitext(file_name)
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_file_name = f"{base_name}_{timestamp}.jpg"
                
                # Upload direto para o Cloudinary
                result = cloudinary.uploader.upload(
                    image_io,
                    public_id=f"cadeURacha/arenas/{os.path.splitext(new_file_name)[0]}",
                    overwrite=True
                )
                
                # Obter a URL do Cloudinary
                cloudinary_url = result['secure_url']
                
                # Salvar apenas no campo foto_url
                instance.foto_url = cloudinary_url
                instance.foto_quadra = None  # Importante: não salvar localmente
                
                # Logs para debug
                print(f"Cloudinary upload result for arena: {result}")
                print(f"Arena image URL set to foto_url: {cloudinary_url}")
                
            except Exception as e:
                print(f"Error uploading arena image to Cloudinary: {e}")
                # Não usamos mais fallback para método tradicional
                # Apenas logar o erro e não salvar a imagem
        
        if commit:
            instance.save()
        
        return instance
        
    def _process_image(self, image):
        # Redimensionar a imagem para um tamanho máximo
        max_size = (1200, 800)
        image.thumbnail(max_size, Image.LANCZOS)
        
        # Se a imagem for PNG com transparência, converter para JPEG com fundo branco
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
            
        return image

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'foto_perfil']  # Add 'foto_perfil' field
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de Usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'})  # Add widget for file input
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('foto_perfil'):
            try:
                # Configurar Cloudinary explicitamente
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )
                
                # Processar a imagem
                image = Image.open(self.cleaned_data['foto_perfil'])
                image = self._process_image(image)
                
                # Preparar para salvar
                image_io = BytesIO()
                image.save(image_io, format='JPEG', quality=90)
                image_io.seek(0)
                
                # Gerar nome de arquivo único
                file_name = self.cleaned_data['foto_perfil'].name
                base_name, ext = os.path.splitext(file_name)
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_file_name = f"{base_name}_{timestamp}.jpg"
                
                # Upload direto para o Cloudinary
                result = cloudinary.uploader.upload(
                    image_io,
                    public_id=f"cadeURacha/perfil/{os.path.splitext(new_file_name)[0]}",
                    overwrite=True
                )
                
                # Obter a URL do Cloudinary
                cloudinary_url = result['secure_url']
                
                # Importante: primeiro definir a URL, depois limpar o campo de arquivo
                instance.foto_url = cloudinary_url
                
                # Não salve o arquivo localmente depois de enviá-lo para o Cloudinary
                # Mas faça isso de forma segura para evitar o erro
                if hasattr(instance, '_foto_perfil_cache'):
                    delattr(instance, '_foto_perfil_cache')
                instance.foto_perfil = None
                
                # Logs para debug
                print(f"Cloudinary upload result: {result}")
                print(f"Image URL set to foto_url: {cloudinary_url}")
                
            except Exception as e:
                print(f"Error uploading to Cloudinary: {e}")
                # Não limpe foto_perfil se o upload falhou
                # Se houver exceção, mantenha o arquivo original
        
        if commit:
            instance.save()
        
        return instance

    def _process_image(self, image):
        # Redimensionar a imagem para um tamanho máximo
        max_size = (500, 500)
        image.thumbnail(max_size, Image.LANCZOS)
        
        # Se a imagem for PNG com transparência, converter para JPEG com fundo branco
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
            
        return image

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha Atual'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova Senha'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a Nova Senha'}))

class JogoForm(forms.ModelForm):
    arena = forms.ModelChoiceField(
        queryset=Arena.objects.all(),
        empty_label="Selecione uma quadra",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Jogo
        fields = ['titulo', 'descricao', 'arena', 'data', 'horario', 'bolas', 'imagem']  # Removido max_jogadores
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'bolas': forms.HiddenInput(attrs={'id': 'qtd-bolas'})
        }

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')
        arena = cleaned_data.get('arena')

        if data and horario and arena:
            # Convert horario to a time object if it's a string
            if isinstance(horario, str):
                try:
                    horario_obj = datetime.datetime.strptime(horario, "%H:%M").time()
                except ValueError:
                    raise forms.ValidationError("Formato de hora inválido, use HH:MM.")
            else:
                horario_obj = horario

            new_start = datetime.datetime.combine(data, horario_obj)
            new_end = new_start + datetime.timedelta(hours=2)

            # Buscar jogos na mesma quadra e data
            conflitos = Jogo.objects.filter(data=data, arena=arena)
            for jogo in conflitos:
                existing_start = datetime.datetime.combine(
                    jogo.data,
                    datetime.datetime.strptime(jogo.horario, "%H:%M").time()
                )
                existing_end = existing_start + datetime.timedelta(hours=2)
                if new_start < existing_end and new_end > existing_start:
                    raise forms.ValidationError(
                        f"Já existe um jogo marcado na quadra '{arena.nome}' no horário selecionado ({horario_obj.strftime('%H:%M')})."
                    )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Tratar o upload da imagem para o Cloudinary
        if self.cleaned_data.get('imagem'):
            try:
                # Configurar Cloudinary explicitamente
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )
                
                # Processar a imagem
                image = Image.open(self.cleaned_data['imagem'])
                # Redimensionar a imagem para um tamanho máximo
                max_size = (1200, 800)
                image.thumbnail(max_size, Image.LANCZOS)
                
                # Se a imagem for PNG com transparência, converter para JPEG com fundo branco
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])
                    image = background
                
                # Preparar para salvar
                image_io = BytesIO()
                image.save(image_io, format='JPEG', quality=90)
                image_io.seek(0)
                
                # Gerar nome de arquivo único
                file_name = self.cleaned_data['imagem'].name
                base_name, ext = os.path.splitext(file_name)
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_file_name = f"{base_name}_{timestamp}.jpg"
                
                # Upload direto para o Cloudinary
                result = cloudinary.uploader.upload(
                    image_io,
                    public_id=f"cadeURacha/rachas/{os.path.splitext(new_file_name)[0]}",
                    overwrite=True
                )
                
                # Obter a URL do Cloudinary
                cloudinary_url = result['secure_url']
                
                # Salvar apenas no campo foto_url
                instance.foto_url = cloudinary_url
                instance.imagem = None  # Importante: não salvar localmente
                
                # Logs para debug
                print(f"Cloudinary upload result for racha: {result}")
                print(f"Racha image URL set to foto_url: {cloudinary_url}")
                
            except Exception as e:
                print(f"Error uploading racha image to Cloudinary: {e}")
                # Não usamos mais fallback para método tradicional
                # Apenas logar o erro e não salvar a imagem
        
        if commit:
            instance.save()
        
        return instance

class CustomUserForm(forms.ModelForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        pattern = re.compile(r'^[a-zA-Z](?!.*__)[a-zA-Z0-9]*(_[a-zA-Z0-9]+)*$')
        
        if len(username) < 4 or len(username) > 20:
            raise forms.ValidationError(
                "O nome de usuário deve ter entre 4 e 20 caracteres."
            )
            
        if not pattern.match(username):
            raise forms.ValidationError(
                "Nome de usuário inválido. Deve começar com uma letra, pode conter letras, "
                "números e sublinhados (não consecutivos e não no início/fim)."
            )
            
        return username