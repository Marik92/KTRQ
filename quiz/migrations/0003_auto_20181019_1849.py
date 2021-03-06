# Generated by Django 2.1.2 on 2018-10-19 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20181019_1840'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='correctvalue',
            options={'verbose_name': 'Правильность ответа', 'verbose_name_plural': 'Правильность ответов'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='answer',
            field=models.CharField(max_length=1024, verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='correctvalue',
            name='value',
            field=models.BooleanField(default=False, verbose_name='Правильность ответа'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.CharField(max_length=200, unique=True, verbose_name='Вопрос'),
        ),
    ]
