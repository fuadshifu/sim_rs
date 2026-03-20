"""
BPJS Service - Skeleton untuk integrasi V-Claim BPJS Kesehatan
Catatan: Implementasi nyata memerlukan API Key dari BPJS Kesehatan
"""

import requests
import json
from datetime import datetime, date
from typing import Optional, Dict, Any, List


class BPJSService:
    """
    Service class untuk komunikasi dengan V-Claim API BPJS Kesehatan.
    Ini adalah skeleton/mock - untuk implementasi nyata diperlukan credentials.
    """

    # Konfigurasi - Diisi dari environment atau config
    BASE_URL = "https://apijkn.bpjs-kesehatan.go.id/vclaim-rest"

    # Development credentials - Ganti dengan credentials asli
    CONSUMER_ID = "YOUR_CONSUMER_ID"
    SECRET_KEY = "YOUR_SECRET_KEY"
    USER_KEY = "YOUR_USER_KEY"

    def __init__(self, config: Optional[Dict[str, str]] = None):
        if config:
            self.CONSUMER_ID = config.get('consumer_id', self.CONSUMER_ID)
            self.SECRET_KEY = config.get('secret_key', self.SECRET_KEY)
            self.USER_KEY = config.get('user_key', self.USER_KEY)
            self.BASE_URL = config.get('base_url', self.BASE_URL)

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers untuk request ke BPJS API"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        signature = self._generate_signature(timestamp)

        return {
            'Content-Type': 'application/json',
            'X-cons-id': self.CONSUMER_ID,
            'X-timestamp': timestamp,
            'X-signature': signature,
            'X-user-key': self.USER_KEY,
            'user_agent': 'SIMRS/1.0'
        }

    def _generate_signature(self, timestamp: str) -> str:
        """Generate signature untuk BPJS API"""
        # Implementasi SHA-256 dengan secret key
        # return hashlib.sha256(f"{self.CONSUMER_ID}{self.SECRET_KEY}{timestamp}".encode()).hexdigest()
        return "MOCK_SIGNATURE"

    def _mock_response(self, data: Any) -> Dict[str, Any]:
        """Generate mock response untuk testing"""
        return {
            "response": {
                "data": data,
                "message": "OK",
                "code": 200
            },
            "metaData": {
                "message": "Sukses",
                "code": "200"
            }
        }

    # ==================== ELIGIBILITAS ====================

    def cek_eligibilitas(self, no_kartu: str, tgl_layanan: date = None) -> Dict[str, Any]:
        """
        Cek eligibilitas peserta BPJS
        Endpoint: /Peserta/nokartu/{noKartu}/tglPelayanan/{tglPelayanan}

        Args:
            no_kartu: Nomor Kartu BPJS
            tgl_layanan: Tanggal layanan (default hari ini)

        Returns:
            Dict dengan data eligibilitas peserta
        """
        if tgl_layanan is None:
            tgl_layanan = date.today()

        tgl_str = tgl_layanan.strftime("%Y-%m-%d")

        # Mock response - karena tidak ada credentials asli
        return self._mock_response({
            "noKartu": no_kartu,
            "nama": "MOCK PASIEN",
            "tglLahir": "1990-01-01",
            "pisa": "1",
            "sex": "L",
            "kelas": "1",
            "kf": "KF",
            "status": "AKTIF",
            "tglAkhirBerlaku": "2025-12-31",
            "tglTerbit": "2020-01-01",
            "provider": {
                "kdProvider": "0001001",
                "nmProvider": "RS EXAMPLE"
            },
            "jenisPeserta": {
                "kdJenis": "1",
                "nmJenis": "PEGAWAI NEGERI"
            },
            "asuransi": {
                "kdAsuransi": "BPJS",
                "nmAsuransi": "BPJS KESEHATAN"
            }
        })

    # ==================== SEP ====================

    def create_sep(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Buat SEP baru
        Endpoint: /SEP/insert

        Args:
            data: Dictionary dengan data SEP
                - noKartu: Nomor kartu BPJS
                - tglSep: Tanggal SEP
                - ppkPelayanan: Kode RS
                - jnsPelayanan: Jenis layanan (1=inap, 2=jalan)
                - klsRawat: Kelas rawat
                - noMR: Nomor MR
                - rujukan: Dictionary rujukan
                - diagnosa: Kode ICD-10
                - catatan: Catatan

        Returns:
            Dict dengan data SEP yang dibuat
        """
        return self._mock_response({
            "sep": {
                "noSep": f"0301{datetime.now().strftime('%Y%m%d')}{'{:06d}'.format(datetime.now().timestamp() % 1000000)}",
                "tglSep": data.get('tglSep', datetime.now().strftime("%Y-%m-%d")),
                "noKartu": data.get('noKartu', ''),
                "ppkPelayanan": data.get('ppkPelayanan', ''),
                "jnsPelayanan": data.get('jnsPelayanan', '2'),
                "klsRawat": data.get('klsRawat', '1'),
                "diagnosa": data.get('diagnosa', ''),
                "catatan": data.get('catatan', ''),
                "status": "200"
            }
        })

    def update_sep(self, no_sep: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data SEP
        Endpoint: /SEP/update
        """
        return self._mock_response({
            "sep": {
                "noSep": no_sep,
                "message": "SEP berhasil diupdate"
            }
        })

    def delete_sep(self, no_sep: str) -> Dict[str, Any]:
        """
        Hapus/Batalkan SEP
        Endpoint: /SEP/delete
        """
        return self._mock_response({
            "sep": {
                "noSep": no_sep,
                "status": "DELETE"
            }
        })

    def get_sep(self, no_sep: str) -> Dict[str, Any]:
        """
        Ambil data SEP
        Endpoint: /SEP/{noSep}
        """
        return self._mock_response({
            "sep": {
                "noSep": no_sep,
                "tglSep": datetime.now().strftime("%Y-%m-%d"),
                "noKartu": "0000000000000",
                "nama": "MOCK PASIEN",
                "kdProvider": "0001001",
                "nmProvider": "RS EXAMPLE",
                "diagnosa": "A09",
                "klsRawat": "1",
                "status": "aktif"
            }
        })

    # ==================== RUJUKAN ====================

    def get_rujukan(self, no_rujukan: str) -> Dict[str, Any]:
        """
        Ambil data rujukan
        Endpoint: /Rujukan/{noRujukan}
        """
        return self._mock_response({
            "rujukan": {
                "noRujukan": no_rujukan,
                "tglRujukan": datetime.now().strftime("%Y-%m-%d"),
                "ppkRujukan": "0001001",
                "nmPpkRujukan": "PUSKESMAS EXAMPLE",
                "ppkPelayanan": "0002001",
                "nmPpkPelayanan": "RS EXAMPLE",
                "diagnosa": {
                    "kode": "A09",
                    "nama": "Gastroenteritis"
                },
                "peserta": {
                    "noKartu": "0000000000000",
                    "nama": "MOCK PASIEN",
                    "tglLahir": "1990-01-01",
                    "sex": "L",
                    "jenisPeserta": {
                        "kdJenis": "1",
                        "nmJenis": "PEGAWAI NEGERI"
                    }
                }
            }
        })

    def get_rujukan_by_no_kartu(self, no_kartu: str) -> Dict[str, Any]:
        """
        Ambil data rujukan berdasarkan nomor kartu
        Endpoint: /Rujukan/List/Peserta/{noKartu}
        """
        return self._mock_response({
            "rujukan": []
        })

    def create_rujukan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Buat rujukan baru
        Endpoint: /Rujukan/insert
        """
        return self._mock_response({
            "rujukan": {
                "noRujukan": f"RUJ{datetime.now().strftime('%Y%m%d')}{'{:06d}'.format(datetime.now().timestamp() % 1000000)}",
                "message": "Rujukan berhasil dibuat"
            }
        })

    # ==================== JADWAL OPERASI ====================

    def get_jadwal_operasi(self, tgl_operasi: date, kode_spesialis: str = None) -> Dict[str, Any]:
        """
        Ambil jadwal operasi
        Endpoint: /JadwalOperasi/list/{tglOperasi}
        """
        return self._mock_response({
            "jadwal": []
        })

    # ==================== KLAIM ====================

    def get_saldo_klaim(self) -> Dict[str, Any]:
        """
        Ambil informasi klaim SEP
        Endpoint: /SEP/KetersediaanKelas
        """
        return self._mock_response({
            "data": {
                "jumlahSEP": 100,
                "jumlahKlaim": 50
            }
        })


# Instance singleton untuk digunakan di routes
bpjs_service = BPJSService()


def init_bpjs_service(config: Dict[str, str] = None):
    """Initialize BPJS service dengan konfigurasi"""
    global bpjs_service
    bpjs_service = BPJSService(config)
    return bpjs_service
