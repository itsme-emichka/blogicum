# Generated by Django 3.2.16 on 2023-07-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20230701_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='post_images', verbose_name='Изображение'),
        ),
    ]
