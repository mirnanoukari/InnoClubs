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
        user = User.objects.filter(email__iexact=self.instance.email).first()
        
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.telegram_alias = validated_data['telegram_alias']
        user.save()
        return user


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


class RetrieveClubsSerializer(serializers.ModelSerializer):

    title = serializers.CharField(allow_blank=False, max_length=100)
    description = serializers.CharField(allow_blank=True)
    head_of_the_club = RUDUserInfoSerializer()
    members = RUDUserInfoSerializer(many=True)

    class Meta:
        model = Club
        fields = ['title',
                  'description',
                  'head_of_the_club',
                  'members']
        read_only_fields = ['head_of_the_club',
                            'members']


class JoinClubSerializer(serializers.ModelSerializer):

    title = serializers.CharField(max_length=100, allow_blank=False)

    class Meta:
        model = Club
        fields = ['title']

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Title is incorrect')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=attrs.get('title')).first()
        if club.members.filter(email__iexact=user.email).count():
            raise serializers.ValidationError('You have already joined this club')
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=validated_data['title']).first()
        club.members.add(user)
        club.save()
        return club


class LeaveClubSerializer(serializers.ModelSerializer):

    title = serializers.CharField(max_length=100, allow_blank=False)

    class Meta:
        model = Club
        fields = ['title']

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Title is incorrect')
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
        club = Club.objects.filter(title__iexact=validated_data['title']).first()
        club.members.remove(user)
        club.save()
        return club


class ChangeClubHeaderSerializer(serializers.ModelSerializer):

    title = serializers.CharField(max_length=100, allow_blank=False)
    head_of_the_club = serializers.EmailField()

    class Meta:
        model = Club
        fields = ['title',
                  'head_of_the_club']

    def validate_title(self, value):
        if not Club.objects.filter(title__iexact=value).count():
            raise serializers.ValidationError('Title is incorrect')
        return value

    def validate(self, attrs):
        print(attrs)
        user = self.context['request'].user
        club = Club.objects.filter(title__iexact=attrs.get('title')).first()
        if club.head_of_the_club != user:
            raise serializers.ValidationError('You are not a club header')
        if not User.objects.filter(email__iexact=attrs.get('head_of_the_club')).count():
            raise serializers.ValidationError('New club header email is incorrect')
        return attrs

    def update(self, instance, validated_data):
        club = Club.objects.filter(title__iexact=validated_data['title']).first()
        new_club_header = User.objects.filter(email__iexact=validated_data['head_of_the_club']).first()
        club.head_of_the_club = new_club_header
        club.save()
        return club
