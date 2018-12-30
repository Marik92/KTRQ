# Generated by Django 2.1.4 on 2018-12-30 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0024_quiz_attempt_choise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='attempt_choise',
            field=models.CharField(choices=[('D', 'Одна попытка в день'), ('M', 'Одна попытка в месяц'), ('Y', 'Одна попытка в год'), ('U', 'Неограниченные попытки')], default='U', max_length=50),
        ),
    ]
