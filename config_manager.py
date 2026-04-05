# config_manager.py
import os
import configparser
from pathlib import Path

class ConfigManager:
    """Manager untuk konfigurasi database"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "config.ini"
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load konfigurasi dari file"""
        if self.config_file.exists():
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # Buat config default jika belum ada
            self.create_default_config()
    
    def create_default_config(self):
        """Buat konfigurasi default"""
        self.config['DATABASE'] = {
            'host': 'localhost',
            'port': '3306',
            'database': 'kasir_db',
            'username': 'root',
            'password': '',
            'api_url': 'http://localhost/kasir_app/backend_api'
        }
        self.save_config()
    
    def save_config(self):
        """Simpan konfigurasi ke file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_db_config(self):
        """Dapatkan konfigurasi database"""
        return {
            'host': self.config.get('DATABASE', 'host', fallback='localhost'),
            'port': self.config.get('DATABASE', 'port', fallback='3306'),
            'database': self.config.get('DATABASE', 'database', fallback='kasir_db'),
            'username': self.config.get('DATABASE', 'username', fallback='root'),
            'password': self.config.get('DATABASE', 'password', fallback=''),
            'api_url': self.config.get('DATABASE', 'api_url', fallback='http://localhost/kasir_app/backend_api')
        }
    
    def update_db_config(self, host, port, database, username, password, api_url):
        """Update konfigurasi database"""
        self.config['DATABASE']['host'] = host
        self.config['DATABASE']['port'] = port
        self.config['DATABASE']['database'] = database
        self.config['DATABASE']['username'] = username
        self.config['DATABASE']['password'] = password
        self.config['DATABASE']['api_url'] = api_url
        self.save_config()
    
    def test_connection(self):
        """Test koneksi database"""
        try:
            import pymysql
            config = self.get_db_config()
            connection = pymysql.connect(
                host=config['host'],
                port=int(config['port']),
                user=config['username'],
                password=config['password'],
                database=config['database'],
                connect_timeout=5
            )
            connection.close()
            return True, "Koneksi berhasil!"
        except pymysql.err.OperationalError as e:
            return False, f"Koneksi gagal: {str(e)}"
        except ImportError:
            return False, "Modul pymysql tidak terinstall. Jalankan: pip install pymysql"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_api_connection(self):
        """Test koneksi API"""
        try:
            import requests
            config = self.get_db_config()
            response = requests.get(f"{config['api_url']}/barang.php", timeout=5)
            if response.status_code == 200:
                return True, "API terhubung!"
            return False, f"API error: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "API tidak dapat dihubungi! Pastikan server berjalan."
        except Exception as e:
            return False, f"API error: {str(e)}"