# Generated by Django 3.1.4 on 2021-03-01 05:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corona', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='문진결과',
            name='questionnaire',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='corona.질문지'),
            preserve_default=False,
        ),
    ]
