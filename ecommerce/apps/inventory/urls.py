from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "printing-worklist",
        staff_member_required(views.PrintingWorkListView.as_view()),
        name="printing_worklist",
    ),
    path(
        "sanding-worklist",
        staff_member_required(views.SandingWorkListView.as_view()),
        name="sanding_worklist",
    ),
    path(
        "sawing-worklist",
        staff_member_required(views.SawingWorkListView.as_view()),
        name="sawing_worklist",
    ),
    path(
        "mounting-worklist",
        staff_member_required(views.MountingWorkListView.as_view()),
        name="mounting_worklist",
    ),
    path(
        "move", staff_member_required(views.move_stock), name="move"
    ),
    path(
        "inspect/", staff_member_required(views.inspect_sku), name="inspect"
    ),
]

