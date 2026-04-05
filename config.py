# config.py
import os
from config_manager import ConfigManager

# Inisialisasi config manager
config_manager = ConfigManager()
db_config = config_manager.get_db_config()

# Konfigurasi API
API_URL = db_config['api_url']

# Data perusahaan
COMPANY_DATA = {
    'nama': 'SARI ALAM',
    'jenis_usaha': 'Supplier / Distributor Kedelai',
    'alamat': 'Jl. Raya Kedelai No. 123, Kecamatan Kedelai, Kota Kedelai',
    'telp': '(021) 12345678',
    'email': 'sarialam@email.com',
    'website': 'www.sarialam.com'
}

# Fungsi untuk mendapatkan konfigurasi database
def get_db_config():
    return db_config

# Fungsi untuk update konfigurasi
def update_db_config(host, port, database, username, password, api_url):
    global API_URL, db_config
    config_manager.update_db_config(host, port, database, username, password, api_url)
    db_config = config_manager.get_db_config()
    API_URL = db_config['api_url']