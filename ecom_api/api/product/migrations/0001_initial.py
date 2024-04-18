# Generated by Django 3.0.4 on 2024-03-26 06:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Catalogue',
            fields=[
                ('CatalogueCode', models.AutoField(primary_key=True, serialize=False)),
                ('CatalogueName', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('CategoryCode', models.AutoField(primary_key=True, serialize=False)),
                ('CategoryName', models.CharField(max_length=250)),
                ('CatalogueCode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Catalogue')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('DateInserted', models.DateTimeField(auto_now_add=True, null=True)),
                ('DateUpdated', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('ProductCode', models.AutoField(primary_key=True, serialize=False)),
                ('SKU', models.CharField(max_length=250, unique=True)),
                ('ProductName', models.TextField()),
                ('ProductDesc', models.TextField(blank=True, null=True)),
                ('URL', models.TextField()),
                ('MainImage', models.TextField()),
                ('CatalogueName', models.CharField(max_length=250)),
                ('CategoryName', models.CharField(max_length=250)),
                ('BrandCode', models.CharField(blank=True, max_length=255, null=True)),
                ('BrandName', models.CharField(max_length=255)),
                ('SubBrandName', models.CharField(blank=True, max_length=255, null=True)),
                ('StockAvailability', models.BooleanField(default=True)),
                ('Offer', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('RegularPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('ModelName', models.CharField(blank=True, max_length=255, null=True)),
                ('ModelNumber', models.CharField(blank=True, max_length=255, null=True)),
                ('RatingValue', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('BestRating', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('ReviewCount', models.IntegerField(default=0)),
                ('CatalogueCode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Catalogue')),
                ('CategoryCode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('DateInserted', models.DateTimeField(auto_now_add=True, null=True)),
                ('DateUpdated', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('VendorCode', models.AutoField(primary_key=True, serialize=False)),
                ('VendorName', models.CharField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SKU', models.CharField(max_length=255)),
                ('Comment', models.TextField()),
                ('Source', models.CharField(max_length=255)),
                ('CommentDate', models.DateField()),
                ('ProductCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SKU', models.CharField(max_length=255)),
                ('Rating1', models.IntegerField()),
                ('Rating2', models.IntegerField()),
                ('Rating3', models.IntegerField()),
                ('Rating4', models.IntegerField()),
                ('Rating5', models.IntegerField()),
                ('ProductCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='VendorCode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Vendor'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SKU', models.CharField(max_length=255)),
                ('image_url', models.TextField()),
                ('ProductCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryLinksMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateInserted', models.DateTimeField(auto_now_add=True, null=True)),
                ('DateUpdated', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('CategoryLink', models.TextField()),
                ('CategoryCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Category')),
                ('VendorCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Vendor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdditionalProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SKU', models.CharField(max_length=255)),
                ('AdditionalProperty', models.TextField()),
                ('ProductCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
    ]
