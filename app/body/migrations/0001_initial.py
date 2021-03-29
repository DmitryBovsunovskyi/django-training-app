# Generated by Django 3.1.7 on 2021-03-26 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MuscleGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000)),
                ('benefits', models.TextField(blank=True, max_length=1000)),
                ('basics', models.TextField(blank=True, max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000)),
                ('basics', models.TextField(blank=True, max_length=1000)),
                ('muscle_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='body.musclegroup')),
            ],
        ),
    ]