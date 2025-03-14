# Generated by Django 4.2.19 on 2025-02-18 18:50

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ('fabrythingapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='Vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='fabrythingapp.vendor'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='Product Image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='pid',
            field=shortuuid.django_fields.ShortUUIDField(alphabet='0123456789abcd', length=10, max_length=20, prefix='prod', unique=True),
        ),
    ]
