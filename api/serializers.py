from rest_framework import serializers

from .models import User


class RUUserInfoSerializer(serializers.ModelSerializer):

    # Items to validate
    first_name = serializers.CharField(max_length=100, allow_blank=True)
    last_name = serializers.CharField(max_length=100, allow_blank=True)
    telegram_alias = serializers.CharField(max_length=100, allow_blank=True)

    class Meta:
        model = User
        fields = ['email',
                  'first_name',
                  'last_name',
                  'telegram_alias']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        user = User.objects.first()
        for obj in User.objects.all():
            if obj.email == self.instance.email:
                user = obj
                break
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.telegram_alias = validated_data['telegram_alias']
        user.save()
        return user
