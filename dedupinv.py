from ecommerce.apps.inventory.models import Stock, ProductInventory, get_stock_by_sku

for p in ProductInventory.objects.filter(
        product_type__name="mounted icon"):
    print(p)
