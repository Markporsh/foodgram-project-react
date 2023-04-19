# Generated by Django 3.2.18 on 2023-04-17 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0003_shoppingcart'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='image',
            field=models.ImageField(default=None, upload_to='recipes/images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='picture',
            field=models.ImageField(upload_to='receipts/images/', verbose_name='Изображение'),
        ),
    ]