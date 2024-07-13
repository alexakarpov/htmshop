import logging
import re
from abc import ABC

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.validators import RegexValidator
from ecommerce.apps.accounts.models import Account

from ecommerce.apps.catalogue.models import Category, Product
from ecommerce.constants import NEW_RE

sku_reg = re.compile("([A-Z]+)-([0-9]+)")
logger = logging.getLogger("django")


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    spec = models.CharField(
        verbose_name="specification", max_length=40, null=True, blank=True
    )
    sku = models.CharField(
        verbose_name="Product SKU",
        help_text="Required",
        max_length=40,
        unique=True,
        primary_key=True,
        validators=[
            RegexValidator(
                regex=NEW_RE,
                message="Not a valid SKU",
                code="nomatch",
            )
        ],
    )

    restock_point = models.PositiveIntegerField(default=0)
    target_amount = models.PositiveIntegerField(default=0)

    wrapping_qty = models.IntegerField(
        default=0, verbose_name="Wrapping room stock"
    )
    sanding_qty = models.IntegerField(
        default=0, verbose_name="Sanding room stock"
    )
    painting_qty = models.IntegerField(
        default=0, verbose_name="Painting room stock"
    )

    weight = models.DecimalField(
        decimal_places=2, max_digits=10, help_text="ounces", default=1
    )  # in ounces
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)

    class Meta:
        verbose_name = "Product Stock Record"
        verbose_name_plural = "Inventory Stock Records"

    # called only from inventory dashboard template
    def get_print_supply_count(self):
        """
        Print supply for a SKU such as A-9 is the number of A-9P units located in wrapping room
        """
        product_sku = self.sku
        print_sku = (
            product_sku + "P" if product_sku[-1] != "P" else product_sku
        )
        logger.debug(f"stock of {product_sku} looking up {print_sku}")
        try:
            print = Stock.objects.get(sku=print_sku)
            return print.wrapping_qty
        except Stock.DoesNotExist:
            logger.warning(f"prints aren't even in stock for {product_sku}")
            return 0

    def is_aseries(self):
        return self.sku[0].upper() == "A"

    def is_print(self):
        return self.sku[-1].upper() == "P"
    
    def is_enlargement(self):
        return self.sku.find("x") != -1

    def is_our_book(self):
        return self.product.category == Category.objects.get(slug='books-monastery')

    def is_incense(self):
        return self.sku[0].upper() == "L"

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
        """
        adjust this stock object's quantity between wrapping, sanding and painting rooms
        move to/from printing supply involves a different SKU so will not be handled by this alone
        """
        logger.debug(
            f"settling move: {qty} of {self} from {from_room} to {to_room}"
        )
        from_room = from_room.lower() if from_room else ""
        to_room = to_room.lower() if to_room else ""

        # increase destination qty
        if to_room.find("wrap") > -1:
            self.wrapping_add(qty)
        elif to_room.find("paint") > -1:
            self.painting_add(qty)
        elif to_room.find("sand") > -1:
            self.sanding_add(qty)
        elif to_room.find("print") > -1:
            self.wrapping_add(qty)
        else:
            logger.debug("to nowhere, nothing to add")

        # decrease source qty
        if from_room.find("wrap") > -1:
            self.wrapping_remove(qty)
        elif from_room.find("paint") > -1:
            self.painting_remove(qty)
        elif from_room.find("sand") > -1:
            self.sanding_remove(qty)
        # on a move from printing to wrapping - we decrease Print SKU, and increase the Mounted
        else:
            logger.debug("from nowhere, nothing to remove")

        return True

    def percentage(self, prct):
        return self.price * prct / 100

    def __str__(self):
        return f"{self.sku} ({self.product.title})"


# class Icon(Stock):
#     pass


def get_or_create_stock_by_sku(sku: str) -> Stock:
    try:
        s = Stock.objects.get(sku=sku.upper())
    except Stock.DoesNotExist:
        # s = Stock.objects.create(sku=sku)
        print(f"Stock for {sku} doesn't exist")
        s = None
    return s


def get_print_supply_by_sku(sku: str) -> Stock:
    return Stock.objects.filter(sku__icontains=sku + "p").first()


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
                    f"{self.sku} doesn't match the expected SKU pattern"
                )
                return True

            omatch = sku_reg.match(other.sku)
            if omatch:
                other_letter, other_num = omatch.groups()
            else:
                logger.error(
                    f"{other.sku} doesn't match the expected SKU pattern"
                )
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
                f"something else blew up matching {self_num} or {other_num}"
            )
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
