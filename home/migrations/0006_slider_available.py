# Generated by Django 2.2.15 on 2020-09-06 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20200906_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='slider',
            name='available',
            field=models.BooleanField(default=True, help_text='Можно отключать слайд без удаления', verbose_name='Активность'),
        ),
    ]