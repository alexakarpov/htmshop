import traceback

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
      product_type table - books, mounted icons, incense - each type will have related specifications.
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
      The product table. This class is meant to be "abstract",
      in a sense that items added to a shopping cart
      will be a Product with Product Specification which are
      required by it's Product Type
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

    def get_variants(self):
        """
        These are actually ProductInventory items related to this Product
        """

        items =  self.productinventory_set.all()
        print(f"{len(items)} SKUs found")
        # print(">>>>>>>>>>>>>>>>")
        # for line in traceback.format_stack():
        #     print(line.strip())
        values = []

        for it in items:
            values.append(it.productspecificationvalue_set.all())

        if values:
            print(f"vals: {values}")
        else:
            print("no vals")

        return values

    def __str__(self):
        return self.title


class ProductSpecification(models.Model):
    """
    The Product Specification Table contains product
    specifiction or features for the product types.
    One Product can come in many variants/specification
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("Required"),
        max_length=55
    )

    class Meta:
        verbose_name = _("specification")
        verbose_name_plural = _("Associated Specifications")

    def __str__(self):
        return f"{self.product_type}.{self.name}"


class ProductInventory(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specifications = models.ManyToManyField(ProductSpecification,
                                            through='ProductSpecificationValue')
    sku = models.CharField(
        verbose_name=_("Product SKU"),
        help_text=_("Required"),
        max_length=10,
        unique=True
    )

    quantity = models.IntegerField()
    weight = models.IntegerField() # in ounces
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)

    class Meta:
        verbose_name = _("Product Inventory Record")
        verbose_name_plural = _("Inventory Records")

    def __str__(self):
        return f"{self.sku} ({self.product})"


class ProductSpecificationValue(models.Model):
    specification = models.ForeignKey(
        ProductSpecification,
        on_delete=models.CASCADE)

    sku = models.ForeignKey(ProductInventory, on_delete=models.CASCADE)

    value = models.CharField(
        max_length=30,
        blank=False
    )

    def __str__(self) -> str:
        return f"{self.sku.product.title} -> {self.specification.name} spec ({self.value})"

    class Meta:
        verbose_name = _("Product spec")
        verbose_name_plural = _("Product specs")


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
