from django.contrib import admin

# from simple_history.admin import SimpleHistoryAdmin
from rangefilter.filters import (
    DateRangeQuickSelectListFilterBuilder,
)

from .models import Order, OrderItem  # , Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["title","quantity"]


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]
    inlines = [
        OrderItemInline,
    ]
    list_filter = (("created_at", DateRangeQuickSelectListFilterBuilder()),)
    search_fields = ("email", "full_name")


# class PaymentAdmin(admin.ModelAdmin):
#     # readonly_fields = ["order"]
#     search_fields = (
#         ("order__full_name",)
#     )


admin.site.register(Order, OrderAdmin)
# admin.site.register(Payment, PaymentAdmin)
