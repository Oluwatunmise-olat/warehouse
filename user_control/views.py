from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, logout, login
from django.core.exceptions import ObjectDoesNotExist
from user_control.serializers import RegisterSerializer , ChangePasswordSerializer, LoginSerializer
from user_control.models import CustomUser


class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        try:
            user = authenticate(request, username=serialized_data.validated_data["email"], password=serialized_data.validated_data["password"])
        except ValueError:
            return Response({"message": "Invalid Login credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
        else:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Login successful", "data":{
                'name': user.get_full_name(),
                'token': token.key
            }}, status=status.HTTP_200_OK)
            
class LogoutView(APIView):
    permission_class = [IsAuthenticated]
    authentication_class = [TokenAuthentication]
    def get(self, request):
        Token.objects.get(user=request.user).delete()
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_class = [IsAuthenticated,]
    authentication_class = [TokenAuthentication,]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        user = request.user
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        password = serialized_data.validated_data["password_one"]
        user = CustomUser.objects.get(id=user.id)
        user.set_password(password)
        user.save()
        return Response({"message": "Password Updated"}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        serialized_data = self.serializer_class(data=data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.data
        
        user = CustomUser.objects.create(
            first_name=serialized_data["first_name"],
            last_name=serialized_data["last_name"],
            email=serialized_data["email"],
            role = "Worker"
        )

        user.set_password(serialized_data["password_one"])
        user.save()
        
        return Response({"message": "Account Created Successfully"}, status=status.HTTP_201_CREATED)