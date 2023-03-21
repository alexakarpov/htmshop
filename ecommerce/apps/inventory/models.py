import re
import logging
from abc import ABC
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from ecommerce.apps.catalogue.models import Product

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


class ProductInventory(models.Model):
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

    # quantity = models.IntegerField()
    restock_point = models.PositiveIntegerField(blank=True, null=True)
    target_amount = models.PositiveIntegerField(blank=False, null=False)

    weight = models.DecimalField(
        decimal_places=2, max_digits=10, help_text="ounces"
    )  # in ounces
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Product Inventory Record")
        verbose_name_plural = _("Inventory Records")

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

    sku = models.ForeignKey(ProductInventory, on_delete=models.CASCADE)

    value = models.CharField(max_length=30, blank=False)

    def __str__(self) -> str:
        return f"{self.value}"

    class Meta:
        verbose_name = _("Product spec")
        verbose_name_plural = _("Product specs")


class Room(models.Model):
    name = models.CharField(verbose_name="Room name", max_length=20)
    slug = models.CharField(verbose_name="Room slug", max_length=20)

    def __str__(self) -> str:
        return self.name

    def get_stock_by_sku(self, sku):
        """
        this gets an exact stock by sku
        """
        try:
            return self.stock_set.get(productinv__sku=sku)
        except Stock.DoesNotExist:
            return None

    def get_print_supply_by_sku(self, sku):
        """
        this will get the [unique] print stock for this sku (icon)
        """
        return self.stock_set.filter(
            productinv__sku__icontains=sku + "p"
        ).first()

    def get_stock_by_type(self, type: str):
        return self.stock_set.filter(
            productinv__product_type__name__icontains=type
        )


class Stock(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    productinv = models.ForeignKey(
        ProductInventory,
        on_delete=models.CASCADE,
        verbose_name="Product Inventory",
    )
    quantity = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.productinv.sku} X {self.quantity} in {self.room}"


class WorkItem(ABC):
    def __init__(self, sku, title):
        self.sku = sku
        self.title = title


class PrintingWorkItem(WorkItem):
    def __init__(self, sku, title, qty):
        # print(f"pwi init with {(sku, title, qty)}")
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
                self_letter, self_num =smatch.groups()
            else:
                logger.error(f"{self.sku} doesn't match the expected SKU pattern")
                return True

            omatch = sku_reg.match(other.sku)
            if omatch:
                other_letter, other_num = omatch.groups()
            else:
                logger.error(f"{other.sku} doesn't match the expected SKU pattern")
                return True

            if self_letter > other_letter:
                return False
            if int(self_num) > int(other_num):
                return False

        except ValueError:
            logger.error(f"either {self_num} or {other_num} are not numeric")
            return True
        except:
            logger.error(f"something else blew up matching {self_num} or {other_num}")
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
