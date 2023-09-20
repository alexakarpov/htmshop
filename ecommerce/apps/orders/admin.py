from django.contrib import admin

# from simple_history.admin import SimpleHistoryAdmin
from rangefilter.filters import (
    DateRangeQuickSelectListFilterBuilder,
)

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]
    inlines = [
        OrderItemInline,
    ]
    list_filter = (
        ("created_at", DateRangeQuickSelectListFilterBuilder()),
    )


admin.site.register(Order, OrderAdmin)
