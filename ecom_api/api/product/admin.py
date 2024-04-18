from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import *


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class CatalogueAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('CatalogueCode', 'CatalogueName', )
    list_filter = ('CatalogueName',)
    actions = ["export_as_csv"]


class CategoryAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('CatalogueCode', 'CategoryCode', 'CategoryName')
    list_filter = ('CatalogueCode__CatalogueName',)
    search_fields = ('CategoryName', 'CatalogueCode__CatalogueName')
    actions = ["export_as_csv"]


class CategoryLinksMappingAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'VendorCode', 'CategoryCode', 'CategoryLink')
    list_filter = ('VendorCode__VendorName', 'CategoryCode__CatalogueCode__CatalogueName', 'CategoryCode__CategoryName')
    search_fields = ('VendorCode__VendorName', 'CategoryCode__CategoryName')
    actions = ["export_as_csv"]


class ProductAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('ProductCode', 'SKU', 'URL', 'ProductName', 'CatalogueCode', 'CategoryCode',)
    list_filter = ('VendorCode__VendorName', 'CategoryCode__CatalogueCode__CatalogueName', 'CategoryCode__CategoryName',)
    search_fields = ('SKU','URL')
    actions = ["export_as_csv"]


class ImageAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('ProductCode', 'SKU', 'image_url')
    search_fields = ('SKU',)
    actions = ["export_as_csv"]


class AdditionalPropertyAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('ProductCode', 'SKU', 'AdditionalProperty')
    search_fields = ('AdditionalProperty', 'SKU',)
    actions = ["export_as_csv"]


class RatingAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('ProductCode', 'SKU', 'Rating1','Rating2','Rating3','Rating4','Rating5')
    search_fields = ('SKU',)
    actions = ["export_as_csv"]


class VendorAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('VendorCode', 'VendorName',)
    search_fields = ('VendorName',)
    actions = ["export_as_csv"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Catalogue, CatalogueAdmin)
admin.site.register(Category, CategoryAdmin)
#admin.site.register(CategoryLinksMapping, CategoryLinksMappingAdmin)
admin.site.register(AdditionalProperty, AdditionalPropertyAdmin)
admin.site.register(Image, ImageAdmin)
# admin.site.register(Rating, RatingAdmin)
admin.site.register(Review)
