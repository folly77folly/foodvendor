from rest_framework import serializers
from ..models import Auth

class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auth
        fields = '__all__'
        # fields = ['password',]

    def create(self, validated_data):
        print(validated_data)
        user = super(AuthSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    # def update(self,instance, validated_data):
    #     # user = super(AuthSerializer, self).create(validated_data)
    #     instance.password = validated_data.get('password', instance.password)
    #     # user.set_password(validated_data['password'])
    #     # user.save()
    #     instance.save()
    #     return instance