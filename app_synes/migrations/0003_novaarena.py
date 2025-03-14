# Generated by Django 5.1.3 on 2025-01-04 16:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_synes', '0002_arena'),
    ]

    operations = [
        migrations.CreateModel(
            name='NovaArena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome da Arena')),
                ('latitude', models.FloatField(verbose_name='Latitude')),
                ('longitude', models.FloatField(verbose_name='Longitude')),
                ('endereco', models.CharField(max_length=300, verbose_name='Endereço')),
                ('capacidade', models.IntegerField(blank=True, null=True, verbose_name='Capacidade')),
                ('tipo_esporte', models.CharField(max_length=100, verbose_name='Tipo de Esporte')),
                ('logradouro', models.CharField(blank=True, max_length=255, null=True, verbose_name='Logradouro')),
                ('bairro', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bairro')),
                ('cidade', models.CharField(blank=True, max_length=255, null=True, verbose_name='Cidade')),
                ('estado', models.CharField(blank=True, max_length=255, null=True, verbose_name='Estado')),
                ('regiao', models.CharField(blank=True, max_length=255, null=True, verbose_name='Região')),
                ('cep', models.CharField(blank=True, max_length=20, null=True, verbose_name='CEP')),
                ('pais', models.CharField(blank=True, max_length=255, null=True, verbose_name='País')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True, verbose_name='Ativo')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='novas_arenas_cadastradas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Nova Arena',
                'verbose_name_plural': 'Novas Arenas',
                'ordering': ['-data_cadastro'],
            },
        ),
    ]
