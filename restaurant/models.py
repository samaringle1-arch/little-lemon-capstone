
from django.db import models


class Menu(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()


    def __str__(self):
        return self.title

class Booking(models.Model):
    name = models.CharField(max_length=100)
    no_of_guests = models.PositiveSmallIntegerField()
    booking_date = models.DateTimeField()

    def __str__(self):
        return f"{self.name} - {self.booking_date}"


from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    def __str__(self):
        return f"Cart for {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menuitem = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "menuitem"],
                name="unique_menu_item_per_cart",
            )
        ]

    def __str__(self):
        return f"{self.menuitem.title} x {self.quantity}"


class Order(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        IN_PROGRESS = 1, "In progress"
        COMPLETED = 2, "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    delivery_crew = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
    )
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING,
    )
    total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menuitem = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    def __str__(self):
        return f"Order {self.order_id}: {self.menuitem.title}"
