# root URL config of ecommerce

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from ecommerce.apps.catalogue import views
from ecommerce.apps.shipping import views as sviews
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/",
        include("ecommerce.apps.accounts.urls", namespace="accounts"),
    ),
    path(
        "checkout/",
        include("ecommerce.apps.checkout.urls", namespace="checkout"),
    ),
    path("basket/", include("ecommerce.apps.basket.urls", namespace="basket")),
    path("orders/", include("ecommerce.apps.orders.urls", namespace="orders")),
    path("search/", include("ecommerce.apps.search.urls", namespace="search")),
    path(
        "shipping/",
        include("ecommerce.apps.shipping.urls", namespace="shipping"),
    ),
    path(
        "inventory/",
        include("ecommerce.apps.inventory.urls", namespace="inventory"),
    ),
    path(
        "st-phanurius-book/", views.st_phanurius_book, name="st-phanurius-book"
    ),
    path(
        "product_info.php/products_id/<int:legacy_id>",
        views.legacy_product,
        name="legacy-product",
    ),
    path(
        "product_info.php/cPath/<str:ignored>/products_id/<int:legacy_id>",
        views.legacy_product,
        name="legacy-product-c",
    ),
    path(
        "export/",
        sviews.shipstation,
        name="get_orders",
    ),
    path("", include("ecommerce.apps.catalogue.urls", namespace="catalogue")),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
