from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'created_at']


class CreateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username band.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(role='student', **validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)

    class Meta:
        model = User
        fields = ['full_name', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
