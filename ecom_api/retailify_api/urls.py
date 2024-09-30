from django.urls import path
from .views import *

urlpatterns = [
    # Vendor URLs
    path('vendors/', VendorList.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', VendorDetail.as_view(), name='vendor-detail'),

    # Catalogue URLs
    path('catalogues/', CatalogueList.as_view(), name='catalogue-list'),
    path('catalogues/<int:pk>/', CatalogueDetail.as_view(), name='catalogue-detail'),

    # Category URLs
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),

    # Product URLs
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),

    # Review URLs
    path('reviews/', ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),

    # Image URLs
    path('images/', ImageList.as_view(), name='image-list'),
    path('images/<int:pk>/', ImageDetail.as_view(), name='image-detail'),


    #################### CUSTOM ENDPOINT URLS ######################
    path('custom-products/', CustomProductList.as_view(), name='custom-products-list'),
    path('multiple-retailers-by-category/', ProductsWithMultipleVendorsByCategoryView.as_view(), name='products-with-multiple-retailers'),
    path('compare-products/', CompareProductsView.as_view(), name='compare-products'),
    # path('compare-products-by-name/', CompareProductsByNameView.as_view(), name='compare-products-by-name'),
    # path('compare-products-by-category/', CompareProductsByCategoryView.as_view(), name='compare-products-by-category'),
    # path('compare-products-by-brand/', CompareProductsByBrandView.as_view(), name='compare-products-by-brand'),
    path('all_retailer_names/', AllVendorNames.as_view(), name='all-retailer-names'),
    path('all_brand_names/', AllBrandNames.as_view(), name='all-brand-names'),
    path('all_category_names/', AllCategoryNames.as_view(), name='all-category-names'),
    path('all_catalogue_names/', AllCatalogueNames.as_view(), name='all-catalogue-names'),
    path('all_ourstore_market_names/', AllOurStoreMarketNames.as_view(), name='all-market-names'),

    
    path('product_details_by_category/', ProductDetailsByCategoryView.as_view(), name='product-details-by-category'),
    path('brand-product-category-counts/', CountBrandProductCategoryView.as_view(), name='brand-product-category-counts'),
    path('count-stockavailability/', CountStockAvailabilityView.as_view(), name='count_stockavailability'),
    path('vendor_details_by_category/', VendorDetailsByCategoryView.as_view(), name='vendor-details-by-category'),
    path('vendor_details_by_brand/', VendorDetailsByBrandView.as_view(), name='vendor-details-by-brand'),
    path('vendor_details_by_catalogue/', VendorDetailsByCatalogueView.as_view(), name='vendor-details-by-catalogue'),
    path('instock_products_by_month/', InStockProductsByMonthView.as_view(), name='instock_products_by_month'),
    path('category-price-by-year/', CategoryPriceByYearView.as_view(), name='category-price-by-year'),
    # path('price-intelligence/', IntelligenceProductPriceView.as_view(), name='price-intelligence'),
    path('price-intelligence-higher/', IntelligenceProductPriceHigher.as_view(), name='price-intelligence-higher'),
    path('price-intelligence-lower/', IntelligenceProductPriceLower.as_view(), name='price-intelligence-lower'),
    path('price-intelligence-equal/', IntelligenceProductPriceEqual.as_view(), name='price-intelligence-equal'),
    path('price-intelligence-difference/', IntelligenceProductPriceDifference.as_view(), name='price-intelligence-difference'),

    path('price-intelligence-higher-count/', ProductCountHigher.as_view(), name='price-intelligence-higher-count'),
    path('price-intelligence-lower-count/', ProductCountLower.as_view(), name='price-intelligence-lower-count'),
    path('price-intelligence-equal-count/', ProductCountEqual.as_view(), name='price-intelligence-equal-count'),
    path('price-intelligence-range-count/', ProductCountRange.as_view(), name='price-intelligence-range-count'),    
    # path('testing/', Testing.as_view(), name='testing')

]
