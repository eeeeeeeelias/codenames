# Generated by Django 3.1.3 on 2020-12-11 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codenames', '0003_auto_20201127_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameresult',
            name='score',
            field=models.IntegerField(choices=[(-9, '0:9'), (-8, '0:8'), (-7, '0:7'), (-6, '0:6'), (-5, '0:5'), (-4, '0:4'), (-3, '0:3'), (-2, '0:2'), (-1, '0:1'), (0, '---------'), (1, '1:0'), (2, '2:0'), (3, '3:0'), (4, '4:0'), (5, '5:0'), (6, '6:0'), (7, '7:0'), (8, '8:0')], default=0),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default=('A', 'A'), max_length=1),
        ),
        migrations.AlterField(
            model_name='resulttype',
            name='_auto_score',
            field=models.IntegerField(blank=True, choices=[(-9, '0:9'), (-8, '0:8'), (-7, '0:7'), (-6, '0:6'), (-5, '0:5'), (-4, '0:4'), (-3, '0:3'), (-2, '0:2'), (-1, '0:1'), (0, '---------'), (1, '1:0'), (2, '2:0'), (3, '3:0'), (4, '4:0'), (5, '5:0'), (6, '6:0'), (7, '7:0'), (8, '8:0')], null=True),
        ),
    ]
