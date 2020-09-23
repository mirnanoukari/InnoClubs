from rest_framework import serializers

from .models import UserModel


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = UserModel.objects.create(
            username=validated_data['username'],
            # email=validated_data['email'],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    def validate_username(self, value):
        qs = UserModel.objects.filter(user__username__exact=value)  # include its own instance
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('The user has been already registered')
        return value

    class Meta:
        model = UserModel
        fields = ['user']
        # fields = ['username',
        #           'password',
        #           'email',
        #           'first_name',
        #           'last_name']
        # read_only_fields = ['email',
        #                     'first_name',
        #                     'last_name']


