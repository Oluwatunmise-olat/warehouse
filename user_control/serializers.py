from rest_framework import serializers
from user_control.models import CustomUser

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password_one = serializers.CharField(required=True)
    password_two = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    def validate(self, data):
        if data["password_one"] != data["password_two"]:
            raise serializers.ValidationError({'password': 'password mismatch'})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    # add check for old password
    # old_password = serializers.CharField()
    password_one = serializers.CharField()
    password_two = serializers.CharField()

    def validate(self, data):
        if data["password_one"] != data["password_two"]:
            raise serializers.ValidationError({'password': 'password mismatch'})
        return data