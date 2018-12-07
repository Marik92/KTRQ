# Generated by Django 2.1.2 on 2018-12-05 08:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0010_question_explanation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Департамент/Служба/Отдел')),
            ],
            options={
                'verbose_name': 'Департамент/Служба/Отдел',
                'verbose_name_plural': 'Департамент/Служба/Отдел',
            },
        ),
        migrations.CreateModel(
            name='Filial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Филиал')),
            ],
            options={
                'verbose_name': 'Филиал',
                'verbose_name_plural': 'Филиалы',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Должность',
                'verbose_name_plural': 'Должности',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100, unique=True, verbose_name='Город/Село')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Department', verbose_name='Департамент/Служба/Отдел')),
                ('filial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Filial', verbose_name='Филиал')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Position', verbose_name='Должность')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='filial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Filial', verbose_name='Филиал'),
        ),
    ]