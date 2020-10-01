from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import User, Club


class RUDUserInfoSerializer(serializers.ModelSerializer):
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
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.telegram_alias = validated_data['telegram_alias']
        instance.save()
        return instance


class CreateClubSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, allow_blank=False)
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = Club
        fields = ['title',
                  'description']
        validators = [UniqueTogetherValidator(
            queryset=Club.objects.all(),
            fields=['title'],
            message='There is already a club with such title')
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        club = Club(title=validated_data['title'],
                    description=validated_data['description'],
                    head_of_the_club=user)
        club.save()
        club.members.add(user)
        return club


class RetrieveClubsSerializer(serializers.Serializer):

    title = serializers.CharField(allow_blank=False, max_length=100)
    description = serializers.CharField(allow_blank=True, required=False)
    head_of_the_club = RUDUserInfoSerializer(required=False, read_only=True)
    members = RUDUserInfoSerializer(many=True, required=False, read_only=True)

    new_title = serializers.CharField(allow_blank=False,
                                      max_length=100,
                                      required=False)
    new_description = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        pass

    def validate_new_title(self, value):
        obj = Club.objects.filter(title__iexact=value)
        obj = obj.exclude(title__iexact=self.instance.title)
        if obj.count():
            raise serializers.ValidationError('There is already a club with such title')
        return value

    def update(self, instance, validated_data):
        instance.title = validated_data['new_title']
        instance.description = validated_data['new_description']
        instance.save()
        return instance


class JoinClubSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, allow_blank=False)

    class Meta:
        model = Club
        fields = ['title']

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Club title is incorrect')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=attrs.get('title')).first()
        if club.members.filter(email__iexact=user.email).count():
            raise serializers.ValidationError('You have already joined this club')
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.members.add(user)
        instance.save()
        return instance


class LeaveClubSerializer(serializers.ModelSerializer):

    title = serializers.CharField(max_length=100, allow_blank=False)

    class Meta:
        model = Club
        fields = ['title']

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Club title is incorrect')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=attrs.get('title')).first()
        if not club.members.filter(email__iexact=user.email).count():
            raise serializers.ValidationError('You are not a member of the club')
        if club.head_of_the_club == user:
            raise serializers.ValidationError('You can not leave a club, as you are a head of this club. ' +
                                              'Please delegate your job to another one')
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.members.remove(user)
        instance.save()
        return instance


class ChangeClubHeaderSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=100, allow_blank=False, required=False)
    new_head_of_the_club = serializers.EmailField(allow_blank=False, required=False)

    def create(self, validated_data):
        pass

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Title is incorrect')
        return value

    def validate_new_head_of_the_club(self, value):
        if not User.objects.filter(email__iexact=value).count():
            raise serializers.ValidationError("New club header's email is incorrect")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=attrs.get('title')).first()
        if club.head_of_the_club != user:
            raise serializers.ValidationError('You are not a club header')
        if not club.members.filter(email__iexact=attrs.get('new_head_of_the_club')).count():
            raise serializers.ValidationError('New club header have to join this club')
        return attrs

    def update(self, instance, validated_data):
        new_club_header = User.objects.filter(email__iexact=validated_data['new_head_of_the_club']).first()
        instance.head_of_the_club = new_club_header
        instance.save()
        return instance
