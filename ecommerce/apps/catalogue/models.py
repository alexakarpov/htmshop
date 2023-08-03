import logging

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

logger = logging.getLogger("django")


class Category(MPTTModel):

    """
    Category Table implimented with mptt
    """

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name=_("Category safe URL"), max_length=255, unique=True
    )

    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        # enforcing that there can only be one category under a parent with same slug
        unique_together = (
            "slug",
            "parent",
        )
        verbose_name_plural = "categories"

    # def __str__(self):
    #     full_path = [self.name]
    #     k = self.parent
    #     while k is not None:
    #         full_path.append(k.name)
    #         k = k.parent
    #     return " -> ".join(full_path[::-1])

    def __str__(self) -> str:
        return (
            f"{self.parent.name} > { self.name }" if self.parent else self.name
        )

    def get_absolute_url(self):
        return reverse("catalogue:category_list", args=[self.slug])


class Product(models.Model):
    """
    The product table. This class is meant to be "abstract",
    in a sense that items added to a shopping cart
    will be a related Stock entity
    """

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.RESTRICT
    )
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("description"), help_text=_("Not Required"), blank=True
    )
    slug = models.SlugField(max_length=255)

    sku_base = models.CharField(max_length=5, verbose_name="SKU base", unique=True)

    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    created_at = models.DateTimeField(
        _("Created at"), auto_now_add=True, editable=False
    )

    users_wishlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="user_wishlist", blank=True
    )

    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_("Upload a product image"),
        upload_to="images/",
        default="images/default.png",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse("catalogue:product_detail", args=[self.slug])

    def get_skus(self):
        """
        These are actually ProductStock items from the inventory app, related to this Product
        """
        logger.debug(f"getting variants for {self}")
        return self.stock_set.filter(product_id=self.id).order_by("price")

    def __str__(self):
        return f"{self.title}"


class ProductImage(models.Model):
    """
    The Product Image table.
    """

    alt_text = models.CharField(
        verbose_name=_("Alternative text"),
        help_text=_("Please add alternative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


@receiver(signals.pre_save, sender=Product)
def product_slug_enforce_lower_case(sender, instance, **kwargs):
    instance.slug = instance.slug.lower()


@receiver(signals.pre_save, sender=Category)
def category_slug_enforce_lower_case(sender, instance, **kwargs):
    instance.slug = instance.slug.lower()
