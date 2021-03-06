# Generated by Django 2.1 on 2018-10-21 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_auto_20181020_1612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={'verbose_name': 'Тест', 'verbose_name_plural': 'Тесты'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name': 'Подкатегория', 'verbose_name_plural': 'Подкатегории'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='correct_or_not',
            field=models.ForeignKey(default='Нет', on_delete=django.db.models.deletion.CASCADE, to='quiz.correctValue'),
        ),
        migrations.AlterField(
            model_name='correctvalue',
            name='value',
            field=models.CharField(max_length=5, verbose_name='Правильность ответа'),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_order',
            field=models.CharField(blank=True, choices=[('content', 'Контент'), ('random', 'Случайно'), ('none', 'None')], default='random', help_text='Правило по которому будут показаны ответы пользователю: случайно, по контенту или none', max_length=30, null=True, verbose_name='Правило вывода ответов'),
        ),
        migrations.AlterField(
            model_name='question',
            name='figure',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d', verbose_name='Рисунок к вопросу'),
        ),
        migrations.AlterField(
            model_name='question',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.SubCategory', verbose_name='Подкатегория'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='sub_category',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Подкатегория'),
        ),
    ]
