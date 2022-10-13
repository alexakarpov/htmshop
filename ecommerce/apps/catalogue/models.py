from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Category Table implimented barebones
    """

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(verbose_name=_(
        "Category safe URL"), max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        # enforcing that there can only be one category under a parent with same slug
        unique_together = (
            "slug",
            "parent",
        )
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return " -> ".join(full_path[::-1])

    def get_absolute_url(self):
        return reverse("catalogue:category_list", args=[self.slug])


class ProductType(models.Model):
    """
      product_type table - books, mounted icons, incense - each type will have related specifications (Attributes).
    """
    name = models.CharField(
        verbose_name=_("Product Type name"),
        help_text=_("Required"),
        max_length=55,
        unique=True)

    class Meta:
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
      The product table. This class is meant to be "abstract" in a sense that items added to a shopping cart
      will be a Product+Product Attributes which are required by it's ProductType 
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_(
        "description"), help_text=_("Not Required"), blank=True)
    slug = models.SlugField(max_length=255)
    # price = models.DecimalField(
    #     verbose_name=_("Price"),
    #     error_messages={
    #         "name": {
    #             "max_length": _("The price must be between 0 and 9999.99."),
    #         },
    #     },
    #     max_digits=6,
    #     decimal_places=2,
    # )
    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    created_at = models.DateTimeField(
        _("Created at"), auto_now_add=True, editable=False)

    users_wishlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="user_wishlist", blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse("catalogue:product_detail", args=[self.slug])

    def __str__(self):
        return self.title


class ProductAttribute(models.Model):
    """
    product_attribute table
    """

    name = models.CharField(
        max_length=55,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("product attribute name"),
        help_text=_("format: required, unique, max-55"),
    )
    description = models.TextField(
        unique=False,
        null=False,
        blank=False,
        verbose_name=_("product attribute description"),
        help_text=_("format: required"),
    )

    def __str__(self):
        return self.name


class ProductTypeAttribute(models.Model):
    """
    Product type attributes link table
    """

    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name="product_attribute",
        on_delete=models.PROTECT,
    )
    product_type = models.ForeignKey(
        ProductType,
        related_name="product_type",
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("product_attribute", "product_type"),)


class ProductAttributeValue(models.Model):
    value = models.CharField(
        verbose_name=_("Specification Value"),
        max_length=20
    )
    spec = models.ForeignKey(ProductTypeAttribute,
                             on_delete=models.CASCADE)
    type = models.ForeignKey('ProductInventory', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.spec.name} -> {self.value}"


class ProductImage(models.Model):
    """
    The Product Image table.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_image")
    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_("Upload a product image"),
        upload_to="images/",
        default="images/default.png",
    )
    alt_text = models.CharField(
        verbose_name=_("Alturnative text"),
        help_text=_("Please add alturnative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


class ProductInventory(models.Model):
    sku = models.CharField(unique=True,
                           max_length=20,
                           blank=False,
                           null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    attributes = models.ManyToManyField(
        ProductTypeAttribute,
        through=ProductAttributeValue
    )
