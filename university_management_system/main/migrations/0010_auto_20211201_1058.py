# Generated by Django 3.1.7 on 2021-12-01 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20211130_2321'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='id',
            field=models.AutoField(auto_created=True,primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='course_code',
            field=models.CharField(max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subject',
            name='id',
            field=models.AutoField(auto_created=True,primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='result',
            name='course_code',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='subject',
            name='subject_name',
            field=models.CharField(max_length=200),
        ),
    ]
