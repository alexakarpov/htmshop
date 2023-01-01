from django.db import models
from django.utils.translation import gettext_lazy as _

from ecommerce.apps.catalogue.models import Product


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
    One Product can have many variants/specification,
    but having more than one spec presents a problem
    in building a web UI with multiple dimensions, so
    for now a single drop-down for one spec solution
    is implemented
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
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
        ProductType, null=False, blank=False, on_delete=models.RESTRICT
    )
    specifications = models.ManyToManyField(
        ProductSpecification, through="ProductSpecificationValue"
    )
    sku = models.CharField(
        verbose_name=_("Product SKU"),
        help_text=_("Required"),
        max_length=10,
        unique=True,
    )

    quantity = models.IntegerField()
    weight = models.IntegerField()  # in ounces
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
