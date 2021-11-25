from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("warehouse_controller.urls")),
    path('api/accounts/', include("user_control.urls")),
]
