from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError

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
        read_only_fields = ('id', 'role', 'full_name')
        extra_kwargs = {
            'username': {'required': False, 'min_length': 3},
            'avatar': {'required': False, 'allow_null': True},
        }

    def validate_username(self, value):
        value = (value or '').strip()
        if len(value) < 3:
            raise serializers.ValidationError('Tên đăng nhập phải có ít nhất 3 ký tự.')
        try:
            UnicodeUsernameValidator()(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        qs = User.objects.filter(username__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Tên đăng nhập đã được sử dụng.')
        return value

    def update(self, instance, validated_data):
        new_avatar = validated_data.get('avatar')
        if new_avatar and instance.avatar:
            instance.avatar.delete(save=False)
        return super().update(instance, validated_data)



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password =serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu hiện tại không đúng.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Mật khẩu xác nhận không khớp."})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user