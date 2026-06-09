import numpy as np
import requests
import re

# 1) CSV dosyasını NumPy ile oku
#NumPy kullanarak CSV dosyasını oku. İlk satır başlık, diğer satırlar veri.
#Input: "data/characters.csv"
#Output: np.ndarray
def read_character_data(file_path: str):
    # skip_header=1 ile başlık satırı atlanır, encoding="utf-8" ile Türkçe karakter desteği sağlanır.
    return np.genfromtxt(file_path, delimiter=",", skip_header=1, dtype=None, encoding="utf-8")


# 2) Veri kümesinden eksik değerleri temizle
#None, boş string ("") veya "NaN" gibi eksik veri olan satırları çıkar.
# Input:
# [
#     ['Johnny', 'Rocker'],
#     ['V', None],
#     ['T-Bug', '']
# ]
# Output:
# [
#     ['Johnny', 'Rocker']
# ] 
def clean_missing_data(data: np.ndarray):
    # Genel bir yaklaşım için metin tabanlı kontrol:
    is_none = (data == None)
    is_empty = (data == "")
    is_nan = (data == "nan") | (data == "NaN") # Metin olarak saklanan NaN'lar için

    # 2. Satır bazında herhangi bir eksik var mı bak (herhangi bir sütunda True varsa o satır True olur)
    mask = np.any(is_none | is_empty | is_nan, axis=1)

    # 3. Maskeyi tersine çevirerek (~mask) sadece eksik olmayan satırları döndür
    return data[~mask]


# 3) Sadece belirli bir karakter sınıfına (örneğin "Netrunner") ait kayıtları döndür
#Belirtilen sınıfa sahip karakterleri getir.
#Input: 
# [
#     ['Johnny', 'Rocker'],
#     ['V', 'Solo'],
#     ['T-Bug', 'Netrunner']
# ], 'Netrunner'
#Output: [['T-Bug', 'Netrunner']]
def filter_by_class(data: np.ndarray, class_name: str):
    # data[:, 1] -> Tüm satırların 2. sütununu (sınıf bilgisini) seçer
    # == class_name -> Aradığımız sınıfa eşit olanları True/False olarak işaretler
    mask = (data[:, 1] == class_name)
    
    # Filtrelenmiş veriyi döndür
    return data[mask]


# 4) Karakter isimlerinden uzun olanları bul (örneğin 10 harften uzun)
# İsmi 10 harften uzun karakterleri bul.
# Input: 
# [
#     ['JohnnySilverhand', 'Rocker'],
#     ['V', 'Solo']
# ]
# Output: 
# ['JohnnySilverhand']
def get_long_names(data: np.ndarray):
    # İsimlerin bulunduğu ilk sütunu (0. indeks) alıp uzunluk kontrolü yaparız
    names = data[:, 0]
    mask = np.array([len(str(name)) > 10 for name in names])
    return names[mask].tolist()


# 5) İsimleri büyük harfe çevir ve yeniden döndür
# Tüm karakter isimlerini büyük harfe çevir (in-place ya da yeni dizi).
# Input: 
# [
#     ['v', 'Solo'],
#     ['t-bug', 'Netrunner']
# ]
# Output:
# [
#     ['V', 'Solo'],
#     ['T-BUG', 'Netrunner']
# ]
def uppercase_names(data: np.ndarray):
    # Veriyi bozmamak için kopya üzerinden işlem yapıyoruz
    updated_data = data.copy()
    # Hem isimleri hem sınıfları büyük harfe çevirir (vektörel işlem)
    updated_data[:, 0] = np.char.upper(updated_data[:, 0].astype(str))
    updated_data[:, 1] = np.char.upper(updated_data[:, 1].astype(str))
    return updated_data


# 6) Sahte bir API'den karakter bilgilerini al
#Verilen URL'e GET isteği at ve response döndür.
#Kullanabileceğin örnel urller:
# https://dummyjson.com/users
# https://jsonplaceholder.typicode.com/users
# https://rickandmortyapi.com/api/character
# Output: requests.Response objesi (status_code + JSON data içeren)
def fetch_character_api_data(api_url: str):
    # Belirtilen adrese HTTP GET isteği gönderir
    return requests.get(api_url)


# 7) API yanıtının geçerli olup olmadığını kontrol et (status code 200 mü?)
# API yanıtı başarılı mı? (status code 200 mü?)
# Input: requests.Response
# Output: True ya da False
def validate_api_response(response: requests.Response):
    # HTTP 200 başarılı bir isteği temsil eder
    return response.status_code == 200


# 8) API’den gelen JSON verisinden "name" alanlarını çek
# Amaç: JSON'dan name alanlarını bir listeye çıkar.
# Input:
# {
#   "users": [
#     {"id": 1, "name": "V"},
#     {"id": 2, "name": "Johnny"}
#   ]
# }
# Output: ['V', 'Johnny']
def extract_names_from_api(json_data: dict):
    # image_7932f4.png dosyasındaki teste göre anahtar 'characters' olmalıdır.
    # .get() kullanarak her iki durumu da (characters veya users) kapsayabiliriz.
    items = json_data.get('characters') or json_data.get('users') or []
    return [item['name'] for item in items]


# 9) Bir string içindeki özel karakterleri temizle (örneğin: %, $, ! vs.)
# String içindeki özel karakterleri temizle (sadece harf ve rakamlar kalsın)
# Input: "Hello@Cyber#punk!"
# Output: "HelloCyberpunk"
def clean_special_characters(s: str):
    # Düzenli ifade (Regex) ile sadece alfanümerik karakterleri tutar
    return re.sub(r'[^a-zA-Z0-9]', '', s)


# 10) Dosyadan gelen verileri ve API'den gelenleri birleştir
# Amaç: Dosyadan gelen veriler ile API'den gelen name verilerini birleştirip liste olarak döndür.
# Input: 
# local_data = np.array([
#     ['Johnny', 'Rocker']
# ])
# api_names = ['V', 'T-Bug']
# Output: 
# [
#     ['Johnny', 'Rocker'],
#     ['V', 'API'],
#     ['T-Bug', 'API']
# ]
def merge_local_and_api_data(local_data: np.ndarray, api_names: list):
    # API'den gelen isimleri 'API' etiketiyle formatlar
    api_entries = [[name, 'API'] for name in api_names]
    # Yerel veriyi listeye çevirip API verisiyle birleştirir
    return local_data.tolist() + api_entries