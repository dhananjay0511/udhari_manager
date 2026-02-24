from django.urls import path
from . import views

app_name = "ledger"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # People
    path("people/", views.PersonListView.as_view(), name="person_list"),
    path("people/add/", views.PersonAddView.as_view(), name="person_add"),
    path("people/<int:pk>/", views.PersonDetailView.as_view(), name="person_detail"),
    path("people/<int:pk>/edit/", views.PersonEditView.as_view(), name="person_edit"),
    path("people/<int:pk>/delete/", views.PersonDeleteView.as_view(), name="person_delete"),
    # Transactions
    path("tx/add/", views.TransactionAddView.as_view(), name="tx_add"),
    path("tx/<int:pk>/edit/", views.TransactionEditView.as_view(), name="tx_edit"),
    path("tx/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="tx_delete"),
]
