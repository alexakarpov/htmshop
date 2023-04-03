from ecommerce.apps.inventory.models import Stock, Stock, get_stock_by_sku

for p in Stock.objects.filter(
        product_type__name="mounted icon"):
    print(p)
