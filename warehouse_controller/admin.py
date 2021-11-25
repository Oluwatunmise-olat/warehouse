from django.contrib import admin

from warehouse_controller.models import Inventory, Activity, TransactionLog

admin.site.register((Inventory, Activity, TransactionLog))