# server.py
# Menjalankan Flask dengan Waitress agar bisa diakses via jaringan

from app import create_app

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    print("=" * 50)
    print("Server SIM RS berjalan...")
    print("Akses dari browser:")
    print("  - Komputer ini: http://localhost:5000")
    print("  - HP/Laptop lain: http://[IP-Komputer]:5000")
    print("=" * 50)
    serve(app, host='0.0.0.0', port=5000)
