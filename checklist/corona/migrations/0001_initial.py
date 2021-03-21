# Generated by Django 3.1.4 on 2021-03-01 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='간부',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='무효', max_length=20)),
                ('password', models.CharField(default='A', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='대대',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='무효', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='사단',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='무효', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='여단',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='무효', max_length=20)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='corona.사단')),
            ],
        ),
        migrations.CreateModel(
            name='질문지',
            fields=[
                ('ownership', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='corona.대대')),
                ('last_revised', models.DateField(auto_now_add=True)),
                ('Q1', models.CharField(max_length=200)),
                ('Q2', models.CharField(max_length=200)),
                ('Q3', models.CharField(max_length=200)),
                ('Q4', models.CharField(max_length=200)),
                ('Q5', models.CharField(max_length=200)),
                ('Q6', models.CharField(max_length=200)),
                ('Q7', models.CharField(max_length=200)),
                ('Q8', models.CharField(max_length=200)),
                ('Q9', models.CharField(max_length=200)),
                ('Q10', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='제출여부',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('battalion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='corona.대대')),
                ('brigade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='corona.여단')),
            ],
        ),
        migrations.CreateModel(
            name='문진결과',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('A1', models.BooleanField()),
                ('A2', models.BooleanField()),
                ('A3', models.BooleanField()),
                ('A4', models.BooleanField()),
                ('A5', models.BooleanField()),
                ('A6', models.BooleanField()),
                ('A7', models.BooleanField()),
                ('A8', models.BooleanField()),
                ('A9', models.BooleanField()),
                ('A10', models.BooleanField()),
                ('is_fine', models.BooleanField()),
                ('battalion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='corona.대대')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='corona.간부')),
            ],
        ),
        migrations.AddField(
            model_name='대대',
            name='brigade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='corona.여단'),
        ),
        migrations.CreateModel(
            name='관리자',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='무효', max_length=20)),
                ('password', models.CharField(default='A', max_length=30)),
                ('access_level', models.CharField(choices=[('Di', '사단장급'), ('Br', '여단장급'), ('Ba', '대대장급')], default='No', help_text='접근권한', max_length=2)),
                ('adminofbatta', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='corona.대대')),
                ('adminofbrig', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='corona.여단')),
                ('adminofdiv', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='corona.사단')),
            ],
        ),
        migrations.AddField(
            model_name='간부',
            name='battalion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='corona.대대'),
        ),
    ]
