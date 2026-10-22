
from rest_framework import serializers
from .models import Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]



from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Menu


class CartItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(
        source="menuitem.title",
        read_only=True,
    )
    unit_price = serializers.DecimalField(
        source="menuitem.price",
        max_digits=6,
        decimal_places=2,
        read_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "menuitem",
            "menuitem_title",
            "quantity",
            "unit_price",
            "subtotal",
        ]

    def get_subtotal(self, obj):
        return obj.menuitem.price * obj.quantity


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(
        source="menuitem.title",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menuitem",
            "menuitem_title",
            "quantity",
            "unit_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "username",
            "delivery_crew",
            "status",
            "total",
            "date",
            "items",
        ]
        read_only_fields = ["id", "username", "total", "date", "items"]
