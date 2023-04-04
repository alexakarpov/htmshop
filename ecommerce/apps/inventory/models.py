import re
import logging
from abc import ABC
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from ecommerce.apps.catalogue.models import Product
from ecommerce.constants import PRODUCT_TYPE_MOUNTED_ICON

sku_reg = re.compile("([A-Z]+)-([0-9]+)")
logger = logging.getLogger("django")


class ProductType(models.Model):
    """
    product_type table - books, mounted icons, incense - each type will have related specifications.
    """

    name = models.CharField(
        verbose_name=_("Product Type name"),
        help_text=_("Required"),
        max_length=55,
        unique=True,
    )

    class Meta:
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    """
    The Product Specification Table contains product
    specifiction or features for the product types.
    A ProductType can have many specification
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"), help_text=_("Required"), max_length=55
    )

    class Meta:
        verbose_name = _("specification")
        verbose_name_plural = _("Associated Specifications")

    def __str__(self):
        return f"{self.product_type}.{self.name}"


class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_type = models.ForeignKey(
        ProductType, null=False, blank=False, on_delete=models.CASCADE
    )
    specifications = models.ManyToManyField(
        ProductSpecification, through="ProductSpecificationValue"
    )
    sku = models.CharField(
        verbose_name=_("Product SKU"),
        help_text=_("Required"),
        max_length=12,
        unique=True,
    )

    restock_point = models.PositiveIntegerField(blank=True, null=True)
    target_amount = models.PositiveIntegerField(blank=False, null=False)

    wrapping_qty = models.IntegerField(
        default=0, verbose_name="Wrapping room stock")
    sanding_qty = models.IntegerField(
        default=0, verbose_name="Sanding room stock")
    painting_qty = models.IntegerField(
        default=0, verbose_name="Painting room stock")

    weight = models.DecimalField(
        decimal_places=2, max_digits=10, help_text="ounces"
    )  # in ounces
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Product Stock Record")
        verbose_name_plural = _("Inventory Stock Records")

    # called only from inventory dashboard template
    def get_print_supply_count(self):
        """
        Print supply for a SKU such as A-9 is the number of A-9P units located in wrapping room
        """
        assert self.product_type.name == PRODUCT_TYPE_MOUNTED_ICON, f"should be executed on {PRODUCT_TYPE_MOUNTED_ICON}, not {self.product_type}"
        product_sku = self.sku
        print_sku = product_sku + 'P'

        try:
            prints = ProductStock.objects.get(sku=print_sku)
            return prints.wrapping_qty
        except ProductStock.DoesNotExist:
            logger.debug(f"prints aren't even in stock for {product_sku}")
            return 0

    def wrapping_add(self, qty: int):
        self.wrapping_qty += qty

    def painting_add(self, qty: int):
        self.painting_qty += qty

    def sanding_add(self, qty: int):
        self.sanding_qty += qty

    def wrapping_remove(self, qty: int):
        self.wrapping_qty -= qty

    def painting_remove(self, qty: int):
        self.painting_qty -= qty

    def sanding_remove(self, qty: int):
        self.sanding_qty -= qty

    def settle_quantities(self, qty: int, from_room: str, to_room: str):
        logger.debug(
            f"settling move of {self.sku}x{qty} from {from_room} to {to_room}")
        from_room = from_room.lower() if from_room else ""
        to_room = to_room.lower() if to_room else ""

        # increase destination qty
        if to_room.find('wrap') > -1:
            self.wrapping_add(qty)
        elif to_room.find('paint') > -1:
            self.painting_add(qty)
        elif to_room.find('sand') > -1:
            self.sanding_add(qty)
        elif to_room.find('print') > -1:
            self.wrapping_add(qty)
        else:
            logger.debug("to nowhere, nothing to add")

        # decrease source qty
        if from_room.find('wrap') > -1:
            self.wrapping_remove(qty)
        elif from_room.find('paint') > -1:
            self.painting_remove(qty)
        elif from_room.find('sand') > -1:
            self.sanding_remove(qty)
        else:
            logger.debug("fromn nowhere, nothing to remove")

        return True

    def __str__(self):
        return f"{self.sku} ({self.product} - {self.product_type})"


class ProductSpecificationValue(models.Model):
    """
    link table for Many-to-Many relationship between ProductSpecification
    and ProductInventory entities
    """

    specification = models.ForeignKey(
        ProductSpecification, on_delete=models.CASCADE
    )

    sku = models.ForeignKey(ProductStock, on_delete=models.CASCADE)

    value = models.CharField(max_length=30, blank=False)

    def __str__(self) -> str:
        return f"{self.value}"

    class Meta:
        verbose_name = _("Product spec")
        verbose_name_plural = _("Product specs")


def get_or_create_stock_by_sku(sku: str) -> ProductStock:
    try:
        s = ProductStock.objects.get(sku=sku.upper())
    except ProductStock.DoesNotExist:
        s = ProductStock.objects.create(sku=sku)
    return s


def get_print_supply_by_sku(sku: str) -> ProductStock:
    return ProductStock.objects.filter(
        sku__icontains=sku + "p"
    ).first()


def get_stock_by_type(type: str) -> ProductStock:
    return ProductStock.objects.filter(
        product_type__name__icontains=type
    )


class WorkItem(ABC):
    def __init__(self, sku, title):
        self.sku = sku
        self.title = title


class PrintingWorkItem(WorkItem):
    def __init__(self, sku, title, qty):
        super().__init__(sku, title)
        self.qty = qty

    def __repr__(self) -> str:
        return f"PWI {self.sku}|{self.title}|{self.qty}"


class MountingWorkItem(WorkItem):
    def __init__(self, sku, title):
        super().__init__(sku, title)

    def __lt__(self, other):
        try:
            smatch = sku_reg.match(self.sku)
            if smatch:
                self_letter, self_num = smatch.groups()
            else:
                logger.error(
                    f"{self.sku} doesn't match the expected SKU pattern")
                return True

            omatch = sku_reg.match(other.sku)
            if omatch:
                other_letter, other_num = omatch.groups()
            else:
                logger.error(
                    f"{other.sku} doesn't match the expected SKU pattern")
                return True

            if self_letter > other_letter:
                return False
            if int(self_num) > int(other_num):
                return False
        except ValueError:
            logger.error(f"either {self_num} or {other_num} are not numeric")
            return True
        except:
            logger.error(
                f"something else blew up matching {self_num} or {other_num}")
            return True
        return True


class SandingWorkItem(WorkItem):
    def __init__(
        self,
        sku,
        title,
        s_qty,  # qty in sanding room
        need,
    ):
        super().__init__(sku, title)
        self.need = need
        self.s_qty = s_qty

    def __repr__(self) -> str:
        return f"{self.sku}|{self.title}|{self.s_qty}|{self.need}"

    def __lt__(self, other):
        return self.need > other.need


class SawingWorkItem(WorkItem):
    def __init__(
        self,
        sku,
        title,
        ps,  # print Supply
        need,
    ):
        super().__init__(sku, title)
        self.need = need
        self.ps = ps

    def __lt__(self, other):
        return self.need > other.need

    def __repr__(self) -> str:
        return f"{self.sku}|{self.title}|{self.ps}|{self.need}"
