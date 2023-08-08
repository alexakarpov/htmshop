from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from ecommerce.apps.inventory.models import Stock, ProductType
from ecommerce.apps.catalogue.models import Product, Category

from ecommerce.constants import (
    BEST_INCENSE_SIZES,
    BETTER_INCENSE_SIZES,
    GOOD_INCENSE_SIZES,
    ICON_PRINT_SIZES,
    INCENSE_CATEGORY_ID,
    INCENSE_TYPE_ID,
    MOUNTED_ICON_SIZES,
    MOUNTED_ICON_TYPE_ID,
    ICONS_CATEGORY_ID,
    ICON_PRINT_TYPE_ID,
)


def generate_icons(icons):
    mounted_type = ProductType.objects.get(id=MOUNTED_ICON_TYPE_ID)
    print_type = ProductType.objects.get(id=ICON_PRINT_TYPE_ID)
    print(f"generating inventory for {len(icons)} icons")

    icon_sizes = MOUNTED_ICON_SIZES

    print_sizes = ICON_PRINT_SIZES

    pcount = ecount = 0
    for icon in icons:
        a_sku = icon.sku_base
        print(f"...for {a_sku}")

        # enlargements
        for size, price, weight in icon_sizes:
            er_sku = a_sku + "." + size + "M"
            try:
                Stock.objects.create(
                    sku=er_sku,
                    product=icon,
                    product_type=mounted_type,
                    weight=weight,
                    price=price,
                    spec=size,
                )
                print(f"created {er_sku}")
                ecount += 1
            except DatabaseError:
                print(f"SKU {er_sku} already exists")

        # prints
        for size, price, weight in print_sizes:
            print_sku = a_sku + "." + size + "P"
            try:
                Stock.objects.create(
                    sku=print_sku,
                    product=icon,
                    product_type=print_type,
                    weight=weight,
                    price=price,
                    spec=f"{size} print",
                )
                print(f"created {print_sku}")
                pcount += 1
            except DatabaseError:
                print(f"SKU {print_sku} already exists")

    return ecount, pcount

def size2spec(size):
    match size:
        case 'A': return "pound"
        case 'B': return "half pound"
        case 'C': return "ounce"
        case _: return "?"

def generate_incense():
    incense_type = ProductType.objects.get(id=INCENSE_TYPE_ID)
    # incense_parent_category = Category.objects.get(id=INCENSE_CATEGORY_ID)

    best_cat = (
        Category.objects.get(slug="best"),
        BEST_INCENSE_SIZES,
    )

    better_cat = (
        Category.objects.get(slug="better"),
        BETTER_INCENSE_SIZES,
    )

    good_cat = (
        Category.objects.get(slug="good"),
        GOOD_INCENSE_SIZES,
    )
    rare_cat = Category.objects.get(slug="rare")
    frank_cat = Category.objects.get(slug="frankincense")

    cats = [good_cat, better_cat, best_cat]

    counts = {}

    for cat, sizes in cats:
        cnt = 0
        for p in cat.product_set.all():
            base_sku = p.sku_base

            for size, weight, price in sizes:
                sized_incense_sku = base_sku + size
                try:
                    Stock.objects.create(
                        sku=sized_incense_sku,
                        product=p,
                        product_type=incense_type,
                        weight=weight,
                        price=price,
                        spec=size2spec(size),
                    )
                    cnt += 1
                except DatabaseError:
                    print(f"SKU {sized_incense_sku} already exists")
            counts[cat.slug] = cnt

    return counts


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        For example Lord Save Me as a 16 x 20 (mounted) the SKU will be A-391.16x20M
        """

        icons_parent_category = Category.objects.get(id=ICONS_CATEGORY_ID)
        icons = []
        for cat in icons_parent_category.get_family():
            print(
                f"found category {cat} with {cat.product_set.count()} products"
            )
            for product in cat.product_set.all():
                icons.append(product)
        e, p = generate_icons(icons)
        print(f"DONE;generated {e} enlargements and {p} prints")
        counts = generate_incense()
        print(
            f"""
generated {counts["good"]} SKUs of Good Incense,
generated {counts["better"]} SKUs of Better Incense,
generated {counts["best"]} SKUS of Best Incense"""
        )
