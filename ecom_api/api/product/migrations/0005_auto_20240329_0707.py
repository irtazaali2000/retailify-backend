# Generated by Django 3.0.4 on 2024-03-29 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20240328_0651'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CategoryLinksMapping',
            new_name='CategoryNameMapping',
        ),
        migrations.RenameField(
            model_name='categorynamemapping',
            old_name='CategoryLink',
            new_name='CategoryName',
        ),
        migrations.AlterField(
            model_name='product',
            name='BrandName',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
