
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from .permissions import IsManagerOrReadOnly
from .models import Menu
from .serializers import MenuSerializer

from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .permissions import IsManager


from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Menu, Order, OrderItem
from .serializers import (
    CartItemSerializer,
    OrderSerializer,
)
from .order_permissions import IsManager, IsDeliveryCrew


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsManagerOrReadOnly]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsManagerOrReadOnly]



from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all().order_by("booking_date")
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



class GroupUserListView(APIView):
    permission_classes = [IsManager]

    group_name = None

    def get(self, request):
        users = User.objects.filter(
            groups__name=self.group_name
        ).distinct()

        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group, _ = Group.objects.get_or_create(
            name=self.group_name
        )
        user.groups.add(group)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class ManagerUsersView(GroupUserListView):
    group_name = "Manager"


class DeliveryCrewUsersView(GroupUserListView):
    group_name = "Delivery Crew"


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("menuitem").all()
        return Response(CartItemSerializer(items, many=True).data)

    def post(self, request):
        menuitem_id = request.data.get("menuitem")
        quantity = request.data.get("quantity", 1)

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            menuitem = Menu.objects.get(pk=menuitem_id)
        except (Menu.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Menu item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            menuitem=menuitem,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff or request.user.groups.filter(
            name="Manager"
        ).exists():
            orders = Order.objects.all()
        elif request.user.groups.filter(name="Delivery Crew").exists():
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)

        orders = orders.prefetch_related("items__menuitem").order_by("-date")
        return Response(OrderSerializer(orders, many=True).data)

    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = list(cart.items.select_related("menuitem").all())
        total = sum(
            (item.menuitem.price * item.quantity for item in cart_items),
            Decimal("0.00"),
        )

        order = Order.objects.create(user=request.user, total=total)

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.menuitem.price,
            )
            for item in cart_items
        ])

        cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_order(self, request, pk):
        try:
            order = Order.objects.prefetch_related(
                "items__menuitem"
            ).get(pk=pk)
        except Order.DoesNotExist:
            return None, Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_manager = (
            request.user.is_staff
            or request.user.groups.filter(name="Manager").exists()
        )
        is_crew = request.user.groups.filter(
            name="Delivery Crew"
        ).exists()

        if (
            not is_manager
            and order.user_id != request.user.id
            and not (is_crew and order.delivery_crew_id == request.user.id)
        ):
            return None, Response(
                {"error": "You do not have permission to access this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return order, None

    def get(self, request, pk):
        order, error = self.get_order(request, pk)
        if error:
            return error
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk):
        order, error = self.get_order(request, pk)
        if error:
            return error

        is_manager = (
            request.user.is_staff
            or request.user.groups.filter(name="Manager").exists()
        )
        is_crew = request.user.groups.filter(
            name="Delivery Crew"
        ).exists()

        if is_manager:
            if "delivery_crew" in request.data:
                crew_id = request.data["delivery_crew"]
                if crew_id is None:
                    order.delivery_crew = None
                else:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        crew = User.objects.get(
                            pk=crew_id,
                            groups__name="Delivery Crew",
                        )
                    except (User.DoesNotExist, ValueError, TypeError):
                        return Response(
                            {"error": "Delivery Crew user not found."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    order.delivery_crew = crew

            if "status" in request.data:
                try:
                    new_status = int(request.data["status"])
                    if new_status not in dict(Order.Status.choices):
                        raise ValueError
                    order.status = new_status
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Status must be 0, 1, or 2."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        elif is_crew:
            if order.delivery_crew_id != request.user.id:
                return Response(
                    {"error": "This order is not assigned to you."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if set(request.data.keys()) != {"status"}:
                return Response(
                    {"error": "Delivery Crew can update only the status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                new_status = int(request.data["status"])
                if new_status not in dict(Order.Status.choices):
                    raise ValueError
                order.status = new_status
            except (ValueError, TypeError):
                return Response(
                    {"error": "Status must be 0, 1, or 2."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"error": "Customers cannot modify orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.save()
        return Response(OrderSerializer(order).data)
