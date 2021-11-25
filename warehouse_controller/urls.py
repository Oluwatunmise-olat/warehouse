from django.urls import path
from warehouse_controller import views

app_name = "warehouse_controller"

urlpatterns = [
    path('create-item/', views.ItemCreateUpdateView.as_view(), name="inventory_item_creation"),
    path('edit/<str:inventory_slug>/', views.ItemCreateUpdateView.as_view(), name="inventory_item_edit"),
    path('create-worker/', views.create_worker_user, name="create_a_worker_user_type"),
    path('stocks/', views.ItemStockView, name="all_items_in_stock"),
    path('activities/<str:inventory_slug>/', views.activities, name="view_activities_per_inventory"),
    path('worker-users/', views.WorkerUsersListView.as_view(), name="all_worker_users"),
    path('transaction/create/', views.TransactionView.as_view(), name="warehouse_transactions"),
    path('transactions/', views.TransactionView.as_view(), name="all_transactions"),
]