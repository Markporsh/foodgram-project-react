# Generated by Django 3.2.18 on 2023-04-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='', verbose_name='Изображение'),
        ),
    ]