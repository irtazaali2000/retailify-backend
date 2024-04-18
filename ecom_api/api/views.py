import csv, io
import logging

from django.shortcuts import render
from django.contrib import messages
from api.product.models import *
from api.product.serializers import *
from django.views.generic import FormView, TemplateView

LOGGER = logging.getLogger(__name__)


class UploadCSV(TemplateView):
    template = "upload_categories.html"

    def get(self, request, *args, **kwargs):
        context = {
            'order': 'Catalogue, Category, CategoryName',
            "categories": CategoryNameMapping.objects.all().order_by('CategoryCode__CatalogueCode__CatalogueName')
        }
        return render(request, self.template, context=context)

    def post(self, request):
        csv_file = request.FILES['file']
        vendor_name = request.POST.get('vendor_name')
        if not vendor_name:
            messages.error(request, "Vendor Not Selected")

        # let's check if it is a csv file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
        data_set = csv_file.read().decode('UTF-8')

        # setup a stream which is when we loop through each line we are able to handle a data in a stream
        io_string = io.StringIO(data_set)
        next(io_string)
        next(io_string)
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            if not column[2]:
                continue

            vendor = {
                "VendorName": vendor_name,
            }

            try:
                vendor_instance = Vendor.objects.get(VendorName=vendor_name)
            except Vendor.DoesNotExist:
                vendor_serializer = VendorSerializer(data=vendor)
                if vendor_serializer.is_valid(raise_exception=True):
                    vendor_instance = vendor_serializer.save()
                    LOGGER.info(f"Vendor Inserted: VendorName: {vendor_instance.VendorName}")

            catalogue = {
                "CatalogueName": column[0].strip(),
                "VendorCode": vendor_instance.VendorCode,
            }

            try:
                catalogue_instance = Catalogue.objects.get(CatalogueName=column[0])
            except Catalogue.DoesNotExist:
                catalogue_serializer = CatalogueSerializer(data=catalogue)
                if catalogue_serializer.is_valid(raise_exception=True):
                    catalogue_instance = catalogue_serializer.save()
                    LOGGER.info(f"Catalogue Inserted: {catalogue['CatalogueName']} | VendorName: {vendor_instance.VendorName}")

            category = {
                "CategoryName": column[1].strip(),
                "CatalogueCode": catalogue_instance.CatalogueCode,
            }
            try:
                category_instance = Category.objects.get(CategoryName=column[1])
            except Category.DoesNotExist:
                category_serializer = CategorySerializer(data=category)
                if category_serializer.is_valid(raise_exception=True):
                    category_instance = category_serializer.save()

                    # LOGGER.info(f"Category Inserted: {category['CategoryName']} | CatalogueName: {category_instance.CatalogueName}")

            categorynamemapping = {
                "VendorCode": vendor_instance.VendorCode,
                "CategoryCode": category_instance.CategoryCode,
                "CategoryName": column[2].strip(),
            }
            try:
                categorynamemapping_instance = CategoryNameMapping.objects.get(CategoryName=column[2].strip())
            except CategoryNameMapping.DoesNotExist:
                categorynamemapping_serializer = CategoryNameMappingSerializer(data=categorynamemapping)
                if categorynamemapping_serializer.is_valid(raise_exception=True):
                    categorynamemapping_serializer.save()
                    LOGGER.info(f"CategoryNameMapping Inserted | "
                                f"VendorName: {vendor_instance.VendorName} | "
                                f"CategoryCode: {categorynamemapping_serializer.initial_data['CategoryCode']} | "
                                f"CategoryName: {categorynamemapping_serializer.initial_data['CategoryName']}"
                                )

        messages.success(request, 'File has been loaded, Successfully!')
        return self.get(request)