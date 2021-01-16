# Generated by Django 3.0.7 on 2021-01-16 16:58

import content.validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_remove_imageattachment_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleImageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField(verbose_name='Source')),
                ('license', models.CharField(blank=True, max_length=200, verbose_name='License')),
                ('image', models.ImageField(upload_to='uploads/contents/%Y/%m/%d/', verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Single Image',
                'verbose_name_plural': 'Single Images',
            },
        ),
        migrations.AlterModelOptions(
            name='pdfcontent',
            options={'verbose_name': 'PDF Content', 'verbose_name_plural': 'PDF Contents'},
        ),
        migrations.RemoveField(
            model_name='imageattachment',
            name='license',
        ),
        migrations.RemoveField(
            model_name='imageattachment',
            name='source',
        ),
        migrations.AlterField(
            model_name='latex',
            name='pdf',
            field=models.FileField(blank=True, upload_to='uploads/contents/%Y/%m/%d/', validators=[content.validator.validate_is_pdf], verbose_name='PDF'),
        ),
        migrations.AlterField(
            model_name='latex',
            name='textfield',
            field=models.TextField(verbose_name='Latex Code'),
        ),
        migrations.AlterField(
            model_name='pdfcontent',
            name='pdf',
            field=models.FileField(blank=True, upload_to='uploads/contents/%Y/%m/%d/', validators=[content.validator.validate_is_pdf], verbose_name='PDF'),
        ),
        migrations.AlterField(
            model_name='textfield',
            name='textfield',
            field=models.TextField(verbose_name='Text'),
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='images', to='content.SingleImageAttachment', verbose_name='Images'),
        ),
    ]