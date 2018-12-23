# Generated by Django 2.1.4 on 2018-12-23 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0016_auto_20181223_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='department',
            field=models.ForeignKey(default=1, limit_choices_to={'filial': models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='filial_article_set', to='quiz.Filial', verbose_name='Филиал')}, on_delete=django.db.models.deletion.CASCADE, related_name='department_article_set', to='quiz.Department', verbose_name='Департамент/Служба/Отдел'),
        ),
        migrations.AlterField(
            model_name='position',
            name='filial',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='filial_article_set', to='quiz.Filial', verbose_name='Филиал'),
        ),
    ]
