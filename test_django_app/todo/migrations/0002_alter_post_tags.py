# Generated by Django 4.0.1 on 2022-01-19 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='+', to='todo.Tag'),
        ),
    ]
