from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from warehouse_controller.models import Activity, Inventory, TransactionLog
from warehouse_controller.serializers import (
    ActivitySerializer, ItemSerializer, TransactionSerializer, UserSerializer, CreateUserSerializer, ItemUpdateSerializer
)
from warehouse_controller.pagination import ListLimitOffsetPagination
from warehouse_controller.permissions import IsPermitted

USER = get_user_model()

class ItemCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser|IsPermitted]
    serializer_class = ItemSerializer
    update_serializer_class = ItemUpdateSerializer

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.data
        item_exist = Inventory.objects.filter(name=serialized_data["name"])
        if not item_exist.exists():
            item = Inventory(
                creator=request.user, price=serialized_data["price"],
                count=serialized_data["count"], name=serialized_data["name"]
            )
            item.save(action="Restock", request=request, amount=serialized_data["count"])
            serialized_data = self.serializer_class(item)
            return Response({"message": "Item Created", "data": serialized_data.data}, status=status.HTTP_201_CREATED)
        return Response("Item Already Exists in Stock. Consider Updating Item Instead", status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        inventory_slug = kwargs.get("inventory_slug")
        queryset = Inventory.objects.filter(slug=inventory_slug)

        if not queryset.exists():
            return Response({"message":"No Inventory Item with provided inventory_slug exists"}, status=status.HTTP_404_NOT_FOUND)
        inventory_inst = queryset.get()

        serialized_data = self.update_serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.data

        if serialized_data.get("name", None): 
            inventory_inst.name = serialized_data["name"]
        if serialized_data.get("price", None): 
            inventory_inst.price = serialized_data["price"]
        if serialized_data.get("count", None): 
            inventory_inst.count = serialized_data["count"]
        
        if serialized_data.get("count", None):
            inventory_inst.save(
                action=serialized_data.get("update_type").title(),
                amount=serialized_data.get("count"),
                description=serialized_data.get("description", None),
                request=request
            )
        else:
            inventory_inst.save(
            action=serialized_data.get("update_type").title(),
            description=serialized_data.get("description", None),
            request=request
            )

        serialized_data = self.serializer_class(inventory_inst)
        return Response({"message":"Inventory Item Updated", "data": serialized_data.data}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_worker_user(request):
    serializer = CreateUserSerializer
    serialized_data = serializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    serialized_data = serialized_data.data
    created_user = USER.objects.create(
        first_name=serialized_data["first_name"],
        last_name=serialized_data["last_name"],
        email=serialized_data["email"],
        role = "Worker"
    )
    created_user.set_password(serialized_data["password_one"])
    created_user.save()
    serialized_data = UserSerializer(created_user)
    return Response({"message":"Worker User Created", "data":serialized_data.data}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_admin_user(request):
    serializer = CreateUserSerializer
    serialized_data = serializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    serialized_data = serialized_data.data
    created_user = USER.objects.create(
        first_name=serialized_data["first_name"],
        last_name=serialized_data["last_name"],
        email=serialized_data["email"],
        role = "Admin",
        is_admin=True,
        is_superuser=True,
        is_staff=True,
        is_worker=False,
)
    created_user.is_admin, 
    serialized_data = UserSerializer(created_user)
    return Response({"message":"Worker User Created", "data":serialized_data.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ItemStockView(request):
    serializer = ItemSerializer
    paginator = ListLimitOffsetPagination()

    queryset = Inventory.all_stock().values()

    paginate_req = paginator.paginate_queryset(queryset, request)
    serialized_data = serializer(paginate_req, many=True)
    paginated_response = paginator.get_paginated_response(serialized_data.data)
    return Response({"data": paginated_response.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def activities(request, inventory_slug):
    query = request.query_params.get("q", None)
    print(inventory_slug)
    serializer = ActivitySerializer
    paginator = ListLimitOffsetPagination()
    queryset = Activity.objects.select_related('performed_by', 'related_item').filter(related_item__slug=inventory_slug)

    if not queryset.exists():
        return Response({"message":"No activity related with provided inventory_slug exists"}, status=status.HTTP_404_NOT_FOUND)
    
    if query:
        queryset = Activity.objects.filter(related_item__slug=inventory_slug, action=query.title())
        paginated_req = paginator.paginate_queryset(queryset, request)
        serialized_data = serializer(paginated_req, many=True)
        paginated_response = paginator.get_paginated_response(serialized_data.data)
        return Response({"data":paginated_response.data}, status=status.HTTP_200_OK)

    paginated_req = paginator.paginate_queryset(queryset, request)
    serialized_data = serializer(paginated_req, many=True)
    paginated_response = paginator.get_paginated_response(serialized_data.data)
    return Response({"data":paginated_response.data}, status=status.HTTP_200_OK)

class WorkerUsersListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = USER.objects.filter(is_worker=True)
    pagination_class = ListLimitOffsetPagination
    serializer_class = UserSerializer

class TransactionView(APIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = ListLimitOffsetPagination

    def get(self, request):
        queryset = TransactionLog.objects.all()

        paginator = self.pagination_class()
        response_data = paginator.paginate_queryset(queryset, request)

        serialized_data = self.serializer_class(response_data, many=True)
        data = paginator.get_paginated_response(serialized_data.data)
        return Response({"data":data.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.data

        serialized_data.update({'sold_by':request.user})

        transaction_inst = TransactionLog.objects.create(
            **serialized_data
        )
        serialized_data = self.serializer_class(transaction_inst)
        return Response({"message":"Transaction Log Created", "data":serialized_data.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def financial_summary(request):
    pass