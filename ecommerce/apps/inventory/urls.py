from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_index, name="inventory_dash"),
    path("print-worklist", staff_member_required(views.PrintWorkListPDFView.as_view()), name='printworklistpdf'),
    path("mount-worklist", views.MountWorkListPDFView.as_view(), name='mountworklistpdf')
]
