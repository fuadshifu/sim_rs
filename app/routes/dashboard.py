from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Pasien, User, Kamar, Obat

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Get statistics
    total_pasien = Pasien.query.filter_by(aktif=True).count()
    total_user = User.query.filter_by(aktif=True).count()

    # Kamar stats
    total_kamar = Kamar.query.filter_by(aktif=True).count()
    kamar_tersedia = 0
    kamar_terpakai = 0
    kamar_maintenance = 0

    for kamar in Kamar.query.filter_by(aktif=True).all():
        for tt in kamar.tempat_tidur:
            if tt.status == 'tersedia':
                kamar_tersedia += 1
            elif tt.status == 'occupied':
                kamar_terpakai += 1
            elif tt.status == 'maintenance':
                kamar_maintenance += 1

    # Obat stats
    obat_rendah = Obat.query.filter(Obat.stok <= Obat.stok_minimum, Obat.aktif==True).count()

    stats = {
        'total_pasien': total_pasien,
        'total_user': total_user,
        'total_kamar': total_kamar,
        'kamar_tersedia': kamar_tersedia,
        'kamar_terpakai': kamar_terpakai,
        'kamar_maintenance': kamar_maintenance,
        'obat_rendah': obat_rendah
    }

    return render_template('dashboard/index.html', stats=stats)

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html')
