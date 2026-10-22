
from django.contrib import admin
from django.urls import path, include
from .views import BookingListCreateView, BookingDetailView
from .views import ManagerUsersView, DeliveryCrewUsersView
from .views import CartView, OrderListCreateView, OrderDetailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("restaurant.urls")),
]

path(
    "groups/manager/users",
    ManagerUsersView.as_view(),
    name="manager-users",
),
path(
    "groups/delivery-crew/users",
    DeliveryCrewUsersView.as_view(),
    name="delivery-crew-users",
),
path("cart/menu-items", CartView.as_view(), name="cart"),
path("orders", OrderListCreateView.as_view(), name="orders"),
path("orders/<int:pk>", OrderDetailView.as_view(), name="order-detail"),