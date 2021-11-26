from django.db import models
from django.conf import settings
from django.db.models.fields import TextField, related

from warehouse_controller.utils import generate_slug

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', )

class Inventory(BaseModel):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="inventory")
    name = models.CharField(max_length=300)
    # image = 
    price = models.FloatField(help_text="Price per item", default=0.0)
    count = models.PositiveIntegerField()
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, action, request, *args, amount=0, description=None, **kwargs):
        self.slug = generate_slug(self)
        super(Inventory, self).save(*args, **kwargs)
        print(self)
        if description:
            return Activity.create_activity(action=action, description=description,
                initiator=request.user, related_item=self, amount=amount
                )
        Activity.create_activity(action=action, amount=amount,initiator=request.user, related_item=self)
        return self

    def format_output(self):
        return {
            'inventory_name': self.name,
            'in_stock': self.count,
            'inventory_price': self.price,
            'inventory_slugname': self.slug,
            'date_created': self.created_at,
            'date_updated': self.updated_at
        }

    @staticmethod
    def all_stock():
        return Inventory.objects.all().order_by('-created_at')


class Activity(BaseModel):
    Actions = (('Restock', 'Restock'), ('Transact', 'Transact'), ('Edit', 'Edit'))
    # Restock means an item was added
    # Transact means an item was removed
    amount = models.PositiveIntegerField(null=True)
    action = models.CharField(Actions, default=None, max_length=10)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="activities")
    related_item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="inventory_action")
    description = models.TextField(null=True, blank=True)

    @staticmethod
    def create_activity(action, initiator, related_item, description=None, amount=0):
        if description:
            object = Activity.objects.create(
                action=action, performed_by=initiator, related_item=related_item, 
                description=description, amount=amount
            )
            return object
        object = Activity.objects.create(
            action=action, amount=amount, performed_by=initiator, related_item=related_item
        )
        return object


class TransactionLog(BaseModel):
    sold_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transaction_log")
    actual_amount = models.FloatField()
    sold_at = models.FloatField()
    sold_to = models.CharField(max_length=50)
    item_name = models.CharField(max_length=300)
    item_count = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)

    def get_financial_summary(self):
        # most bought item
        pass
