from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(SimpleHistoryAdmin):
    readonly_fields = ["created"]
    inlines = [
        OrderItemInline,
    ]

admin.site.register(Order, SimpleHistoryAdmin)
