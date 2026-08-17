from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role', 'phone', 'avatar')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Mật khẩu xác nhận không khớp."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        avatar = validated_data.pop('avatar', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.BUYER),
            phone=validated_data.get('phone', ''),
        )
        if avatar:
            user.avatar = avatar
            user.save(update_fields=['avatar'])
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone', 'role', 'avatar',
            'first_name', 'last_name', 'full_name',
        )
        read_only_fields = ('id', 'username', 'role', 'full_name')