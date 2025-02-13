import logging
import re
from datetime import timezone

import dateutil.parser
import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import User, Company, CompanyName, CompanyKorxona, CompanyKorxonaName
from apps.serializers import UserSerializer, CompanySerializer, CompanyKorxonaSerializer

logger = logging.getLogger(__name__)


def parse_date(date_string):
    if not date_string:
        return None
    try:
        clean_date = re.sub(r'\s*\(.*\)', '', date_string)
        parsed_datetime = dateutil.parser.parse(clean_date)

        return parsed_datetime.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError) as e:
        logger.error(f"Sanani parse qilishda xatolik: {date_string} - {str(e)}")
        return None


class FetchUserAPIView(APIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_user_data_from_api(self, jshshir):
        api_url = f"https://dev-gateway.railwayinfra.uz/api/user/jshshir/{jshshir}"
        TOKEN_API = settings.API_TOKEN

        headers = {
            "Authorization": f"Bearer {TOKEN_API}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        params = {"project": "railmap"}

        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                user_data = response.json().get("data", {})

                return {
                    "login": user_data.get("login", ""),
                    "is_active": user_data.get("isActive", True),
                    "created_at": parse_date(user_data.get("createdAt")),
                    "last_updated_at": parse_date(user_data.get("lastUpdatedAt")),
                    "first_name": user_data.get("firstname", ""),
                    "last_name": user_data.get("lastname", ""),
                    "middle_name": user_data.get("middlename", ""),
                    "full_name": user_data.get("fullname", ""),
                    "avatar": user_data.get("avatar", ""),
                    "domain": user_data.get("domain", ""),
                    "birth_date": parse_date(user_data.get("birthday")),
                    "gender": user_data.get("sex", ""),
                    "education": user_data.get("education", ""),
                    "nationality": user_data.get("nationality", ""),
                    "phone": user_data.get("phone", ""),
                    "birth_place": user_data.get("birthPlace", ""),
                    "current_place": user_data.get("currentPlace", ""),
                    "positions": user_data.get("positions", []),
                    "roles": user_data.get("roles", [])
                }
            else:
                logger.error(f"API xatosi: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"API so‘rovi bajarilmadi: {str(e)}")
            return None

    def create_or_update_user(self, jshshir, password, api_data):

        if not api_data:
            return None, "API ma'lumotlari topilmadi"

        try:
            user, created = User.objects.update_or_create(
                jshshir=jshshir,
                defaults={
                    "password": make_password(password),
                    "login": api_data.get("login", ""),
                    "is_active": api_data.get("is_active", True),
                    "created_at": api_data.get("created_at"),
                    "last_updated_at": api_data.get("last_updated_at"),
                    "first_name": api_data.get("first_name", ""),
                    "last_name": api_data.get("last_name", ""),
                    "middle_name": api_data.get("middle_name", ""),
                    "full_name": api_data.get("full_name", ""),
                    "avatar": api_data.get("avatar", ""),
                    "domain": api_data.get("domain", ""),
                    "birth_date": api_data.get("birth_date"),
                    "gender": api_data.get("gender", ""),
                    "education": api_data.get("education", ""),
                    "nationality": api_data.get("nationality", ""),
                    "phone": api_data.get("phone", ""),
                    "birth_place": api_data.get("birth_place", ""),
                    "current_place": api_data.get("current_place", ""),
                    "positions": api_data.get("positions", []),
                    "roles": api_data.get("roles", [])
                }
            )

            logger.info(f"Foydalanuvchi {jshshir} {'yaratildi' if created else 'yangilandi'}.")

            return user, created
        except IntegrityError as e:
            logger.error(f"User yaratishda xatolik: {str(e)}")
            return None, str(e)

    def post(self, request):
        jshshir = request.data.get("jshshir")
        password = request.data.get("password")

        if not jshshir or not jshshir.isdigit():
            return Response({"error": "JSHSHIR noto‘g‘ri yoki kiritilmagan"}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"error": "Parol majburiy"}, status=status.HTTP_400_BAD_REQUEST)

        api_data = self.get_user_data_from_api(jshshir)

        if not api_data:
            return Response({"error": "Foydalanuvchi ma'lumotlari olinmadi"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = self.create_or_update_user(jshshir, password, api_data)

        if user:
            return Response({
                "message": "Foydalanuvchi yaratildi" if created else "Foydalanuvchi yangilandi",
                "user": UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        else:
            return Response({"error": "Foydalanuvchi yaratilmadi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


API_URL = "https://dev-gateway.railwayinfra.uz/api/company/mtu"


class FetchCompanyDataAPIView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        response = requests.get(API_URL)

        if response.status_code != 200:
            return Response(
                {"error": "Failed to fetch data from API"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            api_data = response.json()
        except ValueError:
            return Response(
                {"error": "Invalid JSON response from API"},
                status=status.HTTP_400_BAD_REQUEST
            )

        """API dan kelayotgan data formatini tekshirish"""
        if not isinstance(api_data, dict) or "data" not in api_data or "data" not in api_data["data"]:
            return Response(
                {"error": "API data format is incorrect", "received": api_data},
                status=status.HTTP_400_BAD_REQUEST
            )

        companies = api_data["data"]["data"]

        saved_companies = []

        for item in companies:
            company, created = Company.objects.update_or_create(
                id=item["id"],
                defaults={
                    "is_active": item["isActive"],
                    "created_at": parse_date(item.get("createdAt")),
                    "last_updated_at": parse_date(item.get("lastUpdatedAt")),
                    "type": item.get("type", ""),
                    "code": item.get("code", ""),
                }
            )

            for name in item.get("names", []):
                CompanyName.objects.update_or_create(
                    company=company,
                    lang=name["lang"],
                    defaults={"data": name["data"]}
                )

            saved_companies.append(company)

        serializer = CompanySerializer(saved_companies, many=True)
        return Response(
            {"message": "Successfully fetched and stored company data.", "data": serializer.data},
            status=status.HTTP_200_OK
        )


COMPANY_API_URL = "https://dev-gateway.railwayinfra.uz/api/company/korxona"


class CompanyKorxonaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        response = requests.get(COMPANY_API_URL)

        if response.status_code == 200:
            data = response.json()

            companies = data.get("data", {}).get("data", [])
            saved_companies = []

            for item in companies:
                company, created = CompanyKorxona.objects.update_or_create(
                    id=item["id"],
                    defaults={
                        "is_active": item["isActive"],
                        "created_at": parse_date(item.get("createdAt")),
                        "last_updated_at": parse_date(item.get("lastUpdatedAt")),
                        "type": item.get("type", "default"),
                    }
                )

                for name in item.get("names", []):
                    CompanyKorxonaName.objects.update_or_create(
                        company_korxona=company,
                        lang=name["lang"],
                        defaults={"data": name["data"]}
                    )

                saved_companies.append(company)

            filter_id = request.query_params.get("id", None)
            filter_is_active = request.query_params.get("is_active", None)

            queryset = CompanyKorxona.objects.all()

            if filter_id:
                queryset = queryset.filter(id=filter_id)

            if filter_is_active:
                is_active_bool = filter_is_active.lower() in ["true", "1"]  # Stringni boolean ga o‘girish
                queryset = queryset.filter(is_active=is_active_bool)

            serializer = CompanyKorxonaSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Failed to fetch data from API"},
            status=status.HTTP_400_BAD_REQUEST
        )


class FilteredCompanyKorxonaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        filter_id = request.query_params.get("id", None)
        filter_is_active = request.query_params.get("is_active", None)

        queryset = CompanyKorxona.objects.all()

        if filter_id is not None:
            try:
                filter_id = int(filter_id)  # `id` ni integerga o‘girish
                queryset = queryset.filter(id=filter_id)
            except ValueError:
                return Response({"error": "Invalid id format"}, status=status.HTTP_400_BAD_REQUEST)

        if filter_is_active is not None:
            is_active_bool = filter_is_active.lower() in ["true", "1"]
            queryset = queryset.filter(is_active=is_active_bool)

        serializer = CompanyKorxonaSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
