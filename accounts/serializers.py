from rest_framework import serializers
from .models import User


def _levels_data(user):
    return [{'id': l.id, 'slug': l.slug, 'name': str(l)} for l in user.levels.all()]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    levels = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'levels', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def get_levels(self, obj):
        return _levels_data(obj)


class UserDetailSerializer(serializers.ModelSerializer):
    levels = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'levels', 'created_at']

    def get_levels(self, obj):
        return _levels_data(obj)


class CreateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    level_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, default=list
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'password', 'level_ids']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username band.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        level_ids = validated_data.pop('level_ids', [])
        user = User(role='student', **validated_data)
        user.set_password(password)
        user.save()
        if level_ids:
            from courses.models import Level
            user.levels.set(Level.objects.filter(id__in=level_ids))
        return user


class UpdateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)
    level_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = User
        fields = ['full_name', 'password', 'level_ids']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        level_ids = validated_data.pop('level_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if level_ids is not None:
            from courses.models import Level
            instance.levels.set(Level.objects.filter(id__in=level_ids))
        return instance
