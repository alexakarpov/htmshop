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
    slug = models.SlugField(verbose_name=_("Category safe URL"), max_length=255, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        # enforcing that there can not be two categories under a parent with same slug

        # __str__ method elaborated later in post.  use __unicode__ in place of

        # __str__ if you are using python 2

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
    ProductType Table will provide a list of the different types
    of products that are for sale.
    """

    name = models.CharField(verbose_name=_("Product Type name"), help_text=_("Required"), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    The Product table contining all product items.
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.RESTRICT)
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_("description"), help_text=_("Not Required"), blank=True)
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(
        verbose_name=_("Price"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 9999.99."),
            },
        },
        max_digits=6,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    users_wishlist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_wishlist", blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    # def get_cat_list(self):
    #     k = self.category  # for now ignore this instance method

    #     breadcrumb = ["dummy"]
    #     while k is not None:
    #         breadcrumb.append(k.slug)
    #         k = k.parent
    #     for i in range(len(breadcrumb) - 1):
    #         breadcrumb[i] = "/".join(breadcrumb[-1 : i - 1 : -1])
    #     return breadcrumb[-1:0:-1]

    def get_absolute_url(self):
        return reverse("catalogue:product_detail", args=[self.slug])

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """
    The Product Image table.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_image")
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
        default="some image alt text",
    )
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


# class ProductAttribute(models.Model):
#     """
#     Product attribute table
#     """

#     product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
#     name = models.CharField(
#         max_length=25,
#         unique=True,
#         null=False,
#         blank=False,
#         verbose_name=_("product attribute name"),
#         help_text=_("format: required, unique, max-25"),
#     )
#     description = models.TextField(
#         unique=False,
#         null=False,
#         blank=False,
#         verbose_name=_("product attribute description"),
#         help_text=_("format: required"),
#     )

#     def __str__(self):
#         return self.name


# class ProductAttributeValue(models.Model):
#     """
#     Product attribute value table
#     """

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="attributes",
#     )
#     product_attribute = models.ForeignKey(
#         ProductAttribute,
#         related_name="product_attribute",
#         on_delete=models.PROTECT,
#     )
#     attribute_value = models.CharField(
#         max_length=25,
#         unique=False,
#         null=False,
#         blank=False,
#         verbose_name=_("attribute value"),
#         help_text=_("format: required, max-25"),
#     )

#     def __str__(self):
#         return f"{self.product_attribute.name} : {self.attribute_value}"
