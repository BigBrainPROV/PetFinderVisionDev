# Generated by Django 4.2 on 2025-06-01 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0007_alter_advertisement_special_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='advertisements/', verbose_name='Фото'),
        ),
    ]
