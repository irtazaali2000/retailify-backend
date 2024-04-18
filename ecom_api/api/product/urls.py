"""ecom_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views.upload_product_delta import ProductUpload
#from .views.upload_product import ProductUpload, StockAvailabilityUpdate
from .views.get_catalogues import CatalogueView
from .views.get_products import ProductsView
# from .views.upload_product_carrefour import ProductUploadCarrefour
# from .views.upload_product_amazon import ProductUploadAmazon
# from .views.upload_product_jumbo import ProductUploadJumbo
# from .views.upload_product_firstcry import ProductUploadFirstCry
# from .views.upload_product_handm import ProductUploadHandM
# from .views.upload_product_boots import ProductUploadBoots
# from .views.upload_product_centrepoint import ProductUploadCentrePoint
# from .views.upload_product_max import ProductUploadMax
# from .views.upload_product_emax import ProductUploadEmax
# from .views.upload_product_namshi import ProductUploadNamshi
# from .views.upload_product_lifepharmacy import ProductUploadLifePharmacy
# from .views.upload_product_asterpharmacy import ProductUploadAsterPharmacy
# from .views.upload_product_sharafdg import ProductUploadSharafDG
# from .views.upload_product_skechers import ProductUploadSkechers
# from .views.upload_product_adidas import ProductUploadAdidas
# from .views.upload_product_pullbear import ProductUploadPullBear
# from .views.upload_product_sssports import ProductUploadSunAndSandSports


urlpatterns = [
    path('upload/', ProductUpload.as_view(), name='upload_product'),
    # path('uploadcarrefour/', ProductUploadCarrefour.as_view(), name='upload_product_carrefour'),
    # path('uploadamazon/', ProductUploadAmazon.as_view(), name='upload_product_amazon'),
    # path('uploadjumbo/', ProductUploadJumbo.as_view(), name='upload_product_jumbo'),
    # path('uploadfirstcry/', ProductUploadFirstCry.as_view(), name='upload_product_firstcry'),
    # path('uploadh_and_m/', ProductUploadHandM.as_view(), name='upload_product_h_and_m'),
    # path('uploadboots/', ProductUploadBoots.as_view(), name='upload_product_boots'),
    # path('uploadcentrepoint/', ProductUploadCentrePoint.as_view(), name='upload_product_centrepoint'),
    # path('uploadmax/', ProductUploadMax.as_view(), name='upload_product_max'),
    # path('uploademax/', ProductUploadEmax.as_view(), name='upload_product_emax'),
    # path('uploadnamshi/', ProductUploadNamshi.as_view(), name='upload_product_namshi'),
    # path('uploadlifepharmacy/', ProductUploadLifePharmacy.as_view(), name='upload_product_lifepharmacy'),
    # path('upload_asterpharmacy/', ProductUploadAsterPharmacy.as_view(), name='upload_product_asterpharmacy'),
    # path('upload_sharafdg/', ProductUploadSharafDG.as_view(), name='upload_product_sharafdg'),
    # path('upload_skechers/', ProductUploadSkechers.as_view(), name='upload_product_skechers'),
    # path('upload_adidas/', ProductUploadAdidas.as_view(), name='upload_product_adidas'),
    # path('upload_pullbear/', ProductUploadPullBear.as_view(), name='upload_product_pullbear'),
    # path('upload_sssports/', ProductUploadSunAndSandSports.as_view(), name='upload_product_sssports'),

    # path('update_stock_availability/', StockAvailabilityUpdate.as_view(), name='update_stock_availability'),
    path('get_catalogues/', CatalogueView.as_view(), name='Get Catalogue by vendor'),
    path('get_products/', ProductsView.as_view(), name='Get Products by Spider Name')
]
