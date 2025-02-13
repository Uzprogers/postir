import requests

url = "https://dev-gateway.railwayinfra.uz/api/company-to-company/mtu-korxonas/{mtuId}"

try:
    response = requests.get(url)
    response.raise_for_status()  # Xatolik bo‘lsa, chiqaradi
    data = response.json()  # JSON formatga o‘girish
    print(data)  # Ma'lumotlarni chop etish
except requests.exceptions.RequestException as e:
    print(f"Xatolik yuz berdi: {e}")
