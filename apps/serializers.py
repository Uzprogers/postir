from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.models import User, Company, CompanyName, CompanyKorxonaName, CompanyKorxona


class UserSerializer(ModelSerializer):
    jshshir = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'jshshir',
            'password',
            'login',
            'is_active',
            'created_at',
            'last_updated_at',
            'first_name',
            'last_name',
            'middle_name',
            'full_name',
            'avatar',
            'domain',
            'birth_date',
            'gender',
            'education',
            'nationality',
            'phone',
            'birth_place',
            'current_place',
            'positions',
            'roles'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'jshshir': {'write_only': True},
            'id': {'read_only': True},
            'login': {'read_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
            'last_updated_at': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'middle_name': {'read_only': True},
            'full_name': {'read_only': True},
            'avatar': {'read_only': True},
            'domain': {'read_only': True},
            'birth_date': {'read_only': True},
            'gender': {'read_only': True},
            'education': {'read_only': True},
            'nationality': {'read_only': True},
            'phone': {'read_only': True},
            'birth_place': {'read_only': True},
            'current_place': {'read_only': True},
            'positions': {'read_only': True},
            'roles': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class CompanyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyName
        fields = ['data', 'lang']


class CompanySerializer(serializers.ModelSerializer):
    names = CompanyNameSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'is_active', 'created_at', 'last_updated_at', 'type', 'code', 'names']


class CompanyKorxonaNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyKorxonaName
        fields = ['data', 'id', 'lang']


class CompanyKorxonaSerializer(serializers.ModelSerializer):
    names = CompanyKorxonaNameSerializer(source='company_names', many=True)

    class Meta:
        model = CompanyKorxona
        fields = ['id', 'is_active', 'created_at', 'last_updated_at', 'type', 'names']
