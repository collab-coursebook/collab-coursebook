# Generated by Django 3.0.4 on 2020-04-07 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pic',
            field=models.ImageField(blank=True, upload_to='profile_pics', verbose_name='Profile picture'),
        ),
    ]