# database_helper.py
import requests
from config import API_URL
from utils import safe_float, safe_int
from config import get_db_config
import traceback

class DatabaseHelper:
    """Helper untuk koneksi ke API"""

    API_URL = None  # Akan diisi dari config

    @classmethod
    def get_api_url(cls):
        if cls.API_URL is None:
            cls.API_URL = get_db_config()['api_url']
        return cls.API_URL
    
    @staticmethod
    def check_connection():
        """Cek koneksi ke API"""
        try:
            response = requests.get(f"{DatabaseHelper.get_api_url()}/barang.php", timeout=3)
            return response.status_code == 200
        except:
            return False
        
    # database_helper.py - Tambahkan method change_password

    @staticmethod
    def change_password(username, old_password, new_password):
        """Change user password"""
        try:
            response = requests.post(f"{API_URL}/change_password.php", json={
                'username': username,
                'old_password': old_password,
                'new_password': new_password
            }, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal mengubah password'}
        except Exception as e:
            print(f"Error change password: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # ==================== PRODUK / BARANG ====================
    
    @staticmethod
    def get_products():
        """Ambil data produk dari API"""
        try:
            response = requests.get(f"{API_URL}/barang.php", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    # Konversi tipe data
                    for p in data:
                        p['harga_jual_kg'] = safe_float(p.get('harga_jual_kg'))
                        p['stok_karung'] = safe_float(p.get('stok_karung'))
                        p['stok_kg'] = safe_float(p.get('stok_kg'))
                        p['berat_per_karung'] = safe_float(p.get('berat_per_karung', 50))
                        p['stok_minimum_karung'] = safe_float(p.get('stok_minimum_karung', 2))
                    return data
                return []
            return []
        except Exception as e:
            print(f"Error get products: {e}")
            return []
        
    @staticmethod
    def login(username, password):
        """Authenticate user"""
        try:
            response = requests.post(
                f"{API_URL}/login.php",
                json={
                    "username": username,
                    "password": password
                },
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal login'}
        except Exception as e:
            print(f"Error login: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def add_product(data):
        """Tambah produk baru"""
        try:
            response = requests.post(f"{API_URL}/barang.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal menambahkan produk'}
        except Exception as e:
            print(f"Error add product: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # ==================== TRANSAKSI ====================
    
    # database_helper.py - Update get_transactions

    @staticmethod
    def get_transactions(start_date=None, end_date=None):
        """Ambil data transaksi dari database dengan id_pelanggan"""
        try:
            url = f"{API_URL}/transaksi.php"
            params = {}
            if start_date and end_date:
                params['start_date'] = start_date
                params['end_date'] = end_date
            elif start_date:
                params['date'] = start_date
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                transactions = response.json()
                if isinstance(transactions, list):
                    parsed = []
                    for t in transactions:
                        parsed.append({
                            'id_transaksi': safe_int(t.get('id_transaksi')),
                            'no_invoice': str(t.get('no_invoice', '-')),
                            'tanggal_transaksi': str(t.get('tanggal_transaksi', '-')),
                            'total_bayar': safe_float(t.get('total_bayar')),
                            'uang_bayar': safe_float(t.get('uang_bayar')),
                            'uang_kembali': safe_float(t.get('uang_kembali')),
                            'kasir': str(t.get('kasir', '-')),
                            'total_karung': safe_float(t.get('total_karung', 0)),
                            'total_kg': safe_float(t.get('total_kg', 0)),
                            'id_pelanggan': safe_int(t.get('id_pelanggan')),  # Tambahkan id_pelanggan
                            'pelanggan': t.get('pelanggan'),  # Tambahkan data pelanggan jika ada
                            'items': t.get('items', [])
                        })
                    return parsed
            return []
        except Exception as e:
            print(f"Error get transactions: {e}")
            return []
    
    @staticmethod
    def get_transaction_by_id(transaction_id):
        """Ambil transaksi berdasarkan ID dengan detail items dan pelanggan"""
        try:
            response = requests.get(f"{API_URL}/transaksi.php?id={transaction_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Parse transaction
                transaction = data.get('transaction', {})
                details = data.get('details', [])
                
                # Hitung total
                total_karung = 0
                total_kg = 0
                items = []
                
                for d in details:
                    karung = safe_float(d.get('jumlah_karung', 0))
                    kg = safe_float(d.get('jumlah_kg', 0))
                    total_karung += karung
                    total_kg += kg
                    
                    items.append({
                        'brand': d.get('brand', '-'),
                        'jumlah_karung': karung,
                        'jumlah_kg': kg,
                        'harga_per_karung': safe_float(d.get('subtotal', 0)) / karung if karung > 0 else 0,
                        'subtotal': safe_float(d.get('subtotal', 0))
                    })
                
                result = {
                    'id_transaksi': safe_int(transaction.get('id_transaksi')),
                    'no_invoice': transaction.get('no_invoice', '-'),
                    'tanggal_transaksi': transaction.get('tanggal_transaksi', '-'),
                    'total_bayar': safe_float(transaction.get('total_bayar')),
                    'uang_bayar': safe_float(transaction.get('uang_bayar')),
                    'uang_kembali': safe_float(transaction.get('uang_kembali')),
                    'kasir': transaction.get('kasir', '-'),
                    'total_karung': total_karung,
                    'total_kg': total_kg,
                    'items': items,
                    'details': details
                }
                
                # Tambahkan data pelanggan jika ada
                if 'pelanggan' in transaction:
                    result['pelanggan'] = transaction.get('pelanggan')
                    result['id_pelanggan'] = transaction.get('id_pelanggan')
                
                return result
            return None
        except Exception as e:
            print(f"Error get transaction by id: {e}")
            return None
        
    # database_helper.py - Tambahkan method untuk get transaction details

    @staticmethod
    def get_transactions_with_details(start_date=None, end_date=None):
        """Ambil data transaksi lengkap dengan detail items"""
        try:
            url = f"{API_URL}/transaksi.php"
            params = {}
            if start_date and end_date:
                params['start_date'] = start_date
                params['end_date'] = end_date
            elif start_date:
                params['date'] = start_date
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                transactions = response.json()
                if isinstance(transactions, list):
                    # Untuk setiap transaksi, ambil detail items
                    for t in transactions:
                        trans_id = t.get('id_transaksi')
                        if trans_id:
                            # Ambil detail items untuk transaksi ini
                            detail_response = requests.get(f"{API_URL}/transaksi.php?id={trans_id}", timeout=3)
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                t['items'] = detail_data.get('details', [])
                            else:
                                t['items'] = []
                        else:
                            t['items'] = []
                    return transactions
            return []
        except Exception as e:
            print(f"Error get transactions with details: {e}")
            return []

    @staticmethod
    def get_transaction_detail(transaction_id):
        """Ambil detail transaksi berdasarkan ID"""
        try:
            response = requests.get(f"{API_URL}/transaksi.php?id={transaction_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('details', [])
            return []
        except Exception as e:
            print(f"Error get transaction detail: {e}")
            return []
    
    @staticmethod
    def get_all_transactions_with_details(limit=100):
        """Ambil semua transaksi lengkap dengan detail items"""
        try:
            # Ambil semua transaksi
            response = requests.get(f"{API_URL}/transaksi.php", timeout=5)
            if response.status_code == 200:
                transactions = response.json()
                if isinstance(transactions, list):
                    # Untuk setiap transaksi, ambil detail items
                    for t in transactions:
                        trans_id = t.get('id_transaksi')
                        if trans_id:
                            detail_response = requests.get(f"{API_URL}/transaksi.php?id={trans_id}", timeout=3)
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                t['items'] = detail_data.get('details', [])
                            else:
                                t['items'] = []
                        else:
                            t['items'] = []
                    return transactions
            return []
        except Exception as e:
            print(f"Error get all transactions with details: {e}")
            return []
    
    @staticmethod
    def save_transaction(items, total, bayar, kembali, kasir, id_pelanggan=None):
        """Simpan transaksi dengan id_pelanggan"""
        try:
            data = {
                'items': items,
                'total_bayar': total,
                'uang_bayar': bayar,
                'uang_kembali': kembali,
                'kasir': kasir
            }
            
            # Tambahkan id_pelanggan jika ada
            if id_pelanggan:
                data['id_pelanggan'] = id_pelanggan
            
            response = requests.post(f"{API_URL}/transaksi.php", json=data, timeout=10)
            
            # Cek status code
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result
                except Exception as json_error:
                    print(f"JSON parse error: {json_error}")
                    print(f"Response text: {response.text}")
                    return {
                        'status': 'error', 
                        'message': 'Respons dari server tidak valid'
                    }
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response text: {response.text}")
                return {
                    'status': 'error', 
                    'message': f'Gagal menyimpan transaksi (HTTP {response.status_code})'
                }
                
        except requests.exceptions.ConnectionError:
            print("Connection error")
            return {
                'status': 'error', 
                'message': 'Tidak dapat terhubung ke server! Pastikan server berjalan.'
            }
        except requests.exceptions.Timeout:
            print("Timeout error")
            return {
                'status': 'error', 
                'message': 'Waktu koneksi habis! Periksa jaringan Anda.'
            }
        except Exception as e:
            print(f"Error save transaction: {e}")
            # import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
    
    # ==================== PELANGGAN ====================
    
    @staticmethod
    def get_customers():
        """Ambil semua data pelanggan"""
        try:
            response = requests.get(f"{API_URL}/pelanggan.php", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    return data
            return []
        except Exception as e:
            print(f"Error get customers: {e}")
            return []
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """Ambil data pelanggan berdasarkan ID"""
        try:
            response = requests.get(f"{API_URL}/pelanggan.php?id={customer_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Konversi tipe data
                    data['poin'] = safe_float(data.get('poin', 0))
                    data['total_belanja'] = safe_float(data.get('total_belanja', 0))
                    return data
            return None
        except Exception as e:
            print(f"Error get customer by id: {e}")
            return None
    
    @staticmethod
    def add_customer(data):
        """Tambah pelanggan baru"""
        try:
            response = requests.post(f"{API_URL}/pelanggan.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal menambahkan pelanggan'}
        except Exception as e:
            print(f"Error add customer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def update_customer(customer_id, data):
        """Update pelanggan"""
        try:
            data['id_pelanggan'] = customer_id
            response = requests.put(f"{API_URL}/pelanggan.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal update pelanggan'}
        except Exception as e:
            print(f"Error update customer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def delete_customer(customer_id):
        """Hapus pelanggan"""
        try:
            response = requests.delete(f"{API_URL}/pelanggan.php?id={customer_id}", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal hapus pelanggan'}
        except Exception as e:
            print(f"Error delete customer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # ==================== LAPORAN ====================
    
    @staticmethod
    def get_report(periode='harian', start_date=None, end_date=None):
        """Ambil laporan penjualan"""
        try:
            url = f"{API_URL}/rekap.php"
            params = {'periode': periode}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'data': [], 'summary': {}}
        except Exception as e:
            print(f"Error get report: {e}")
            return {'data': [], 'summary': {}}
        
    @staticmethod
    def update_customer_poin(customer_id, poin_tambah, total_belanja_tambah):
        """Update customer poin and total belanja"""
        try:
            response = requests.put(
                f"{API_URL}/pelanggan.php?action=update_poin",
                json={
                    'id_pelanggan': customer_id,
                    'poin_tambah': poin_tambah,
                    'total_belanja_tambah': total_belanja_tambah
                },
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal update poin'}
        except Exception as e:
            print(f"Error update customer poin: {e}")
            return {'status': 'error', 'message': str(e)}
        
    @staticmethod
    def update_product(product_id, data):
        """Update produk"""
        try:
            response = requests.put(f"{API_URL}/barang.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal update produk'}
        except Exception as e:
            print(f"Error update product: {e}")
            return {'status': 'error', 'message': str(e)}
        
    @staticmethod
    def delete_product(product_id):
        """
        Hapus produk berdasarkan ID dengan error handling yang lebih baik
        
        Args:
            product_id (int): ID produk yang akan dihapus
            
        Returns:
            dict: Status hasil operasi dengan format:
                {
                    'status': 'success' or 'error',
                    'message': 'Pesan hasil operasi',
                    'data': (opsional) data produk yang dihapus
                }
        """
        # Validasi input
        if not product_id or product_id <= 0:
            return {
                'status': 'error',
                'message': 'ID produk tidak valid'
            }
        
        try:
            # Panggil API DELETE
            response = requests.delete(
                f"{API_URL}/barang.php?id={product_id}",
                timeout=10  # Timeout 10 detik
            )
            
            # Cek status HTTP
            if response.status_code == 200:
                result = response.json()
                return result
            elif response.status_code == 404:
                return {
                    'status': 'error',
                    'message': 'Produk tidak ditemukan'
                }
            elif response.status_code == 409:
                return {
                    'status': 'error',
                    'message': 'Produk tidak dapat dihapus karena memiliki riwayat transaksi'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Gagal menghapus produk (HTTP {response.status_code})'
                }
                
        except requests.exceptions.ConnectionError:
            print(f"Error delete product: Connection error")
            return {
                'status': 'error',
                'message': 'Tidak dapat terhubung ke server! Pastikan server berjalan.'
            }
        except requests.exceptions.Timeout:
            print(f"Error delete product: Timeout")
            return {
                'status': 'error',
                'message': 'Waktu koneksi habis! Periksa jaringan Anda.'
            }
        except requests.exceptions.RequestException as e:
            print(f"Error delete product: {e}")
            return {
                'status': 'error',
                'message': f'Kesalahan koneksi: {str(e)}'
            }
        except Exception as e:
            print(f"Error delete product: {e}")
            return {
                'status': 'error',
                'message': f'Terjadi kesalahan: {str(e)}'
            }

    @staticmethod
    def add_stock_log(id_barang, kode_barang, brand, jenis_transaksi, 
                      jumlah_karung, jumlah_kg, stok_sebelum_karung, 
                      stok_sebelum_kg, stok_sesudah_karung, stok_sesudah_kg,
                      keterangan="", no_referensi="", user="Admin"):
        """Tambahkan log stok"""
        try:
            data = {
                'id_barang': id_barang,
                'kode_barang': kode_barang,
                'brand': brand,
                'jenis_transaksi': jenis_transaksi,
                'jumlah_karung': jumlah_karung,
                'jumlah_kg': jumlah_kg,
                'stok_sebelum_karung': stok_sebelum_karung,
                'stok_sebelum_kg': stok_sebelum_kg,
                'stok_sesudah_karung': stok_sesudah_karung,
                'stok_sesudah_kg': stok_sesudah_kg,
                'keterangan': keterangan,
                'no_referensi': no_referensi,
                'user': user
            }
            response = requests.post(f"{API_URL}/log_stok.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal menambahkan log stok'}
        except Exception as e:
            print(f"Error add stock log: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def get_stock_logs(start_date=None, end_date=None, limit=100):
        """Ambil log stok"""
        try:
            url = f"{API_URL}/log_stok.php"
            params = {}
            if start_date and end_date:
                params['start_date'] = start_date
                params['end_date'] = end_date
            elif start_date:
                params['date'] = start_date
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                logs = response.json()
                if isinstance(logs, list):
                    return logs
            return []
        except Exception as e:
            print(f"Error get stock logs: {e}")
            return []
    
    @staticmethod
    def get_stock_logs_by_product(product_id, limit=50):
        """Ambil log stok berdasarkan produk"""
        try:
            response = requests.get(f"{API_URL}/log_stok.php?product_id={product_id}", timeout=5)
            if response.status_code == 200:
                logs = response.json()
                if isinstance(logs, list):
                    return logs
            return []
        except Exception as e:
            print(f"Error get stock logs by product: {e}")
            return []
        
    @staticmethod
    def update_stock(product_id, data):
        """Update stok produk"""
        try:
            response = requests.put(f"{API_URL}/barang.php", json=data, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'status': 'error', 'message': 'Gagal update stok'}
        except Exception as e:
            print(f"Error update stock: {e}")
            return {'status': 'error', 'message': str(e)}