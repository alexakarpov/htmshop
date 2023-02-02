from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_index, name="inventory_dash"),
    path("print-worklist", staff_member_required(views.generate_pdf), name='printworklistpdf'),
    path("print-worklist-html", staff_member_required(views.PrintWorkListHTMLView.as_view()),
    name='printworklisthtml'
    ),

]
