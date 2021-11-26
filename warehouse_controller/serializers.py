from django.db.models.fields import related
from rest_framework import serializers
from user_control.models import CustomUser

from warehouse_controller.models import  Inventory, Activity, TransactionLog

class ActivitySerializer(serializers.ModelSerializer):
    performed_by = serializers.SerializerMethodField(read_only=True)
    related_item = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'

    def get_performed_by(self, obj):
        return obj.performed_by.get_full_name()

    def get_related_item(self, obj):
        return obj.related_item.format_output()

class ItemSerializer(serializers.ModelSerializer):
    inventory_action = ActivitySerializer(read_only=True, many=True)

    class Meta:
        model = Inventory
        fields = ('name', 'price', 'count', "slug", "inventory_action")
        extra_kwargs = {
            "name" : {"required": True},
            "price" : {"required": True},
            "slug" : {"required": False},
            "count" : {"required": True},
        }

class ItemUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    price = serializers.FloatField(required=False)
    count = serializers.IntegerField(required=False)
    update_type = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    def valiate_update_type(self, value):
        update_types = ('transact', 'restock', 'edit')
        if not value.lower() in update_types:
            raise serializers.ValidationError(
                f"Updating an Item must be of either types <{update_types}>"
            )
        return value


class CreateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password_one = serializers.CharField()
    password_two = serializers.CharField()

    def validate(self, attrs):
        if not attrs["password_one"] == attrs["password_two"]:
            return serializers.ValidationError("Password Mismatch")
        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "role", )

class TransactionSerializer(serializers.ModelSerializer):

    sold_by = serializers.SerializerMethodField()

    def get_sold_by(self, obj):
       pass

    class Meta:
        model = TransactionLog
        fields = ('sold_by', 'actual_amount', 'sold_at', 'sold_to', 'item_name', 'item_count', 'description')


