# Generated by Django 2.2.15 on 2020-09-20 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['timestamp'], 'verbose_name': '02: Статья', 'verbose_name_plural': '02: Статьи'},
        ),
        migrations.AlterModelOptions(
            name='pagenewsseo',
            options={'verbose_name': '01: Новости - общая страница', 'verbose_name_plural': '01: Новости - общая страница'},
        ),
    ]
