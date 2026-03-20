from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Billing, BillingDetail, Pembayaran, Pasien, RawatJalan, RawatInap, Resep, ResepDetail, PemeriksaanLab, JenisPemeriksaan
from datetime import datetime
import random

kasir_bp = Blueprint('kasir', __name__, url_prefix='/kasir')

def generate_invoice():
    """Generate unique invoice number"""
    return f'INV-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}'

# ========== BILLING ==========
@kasir_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    query = Billing.query

    if status:
        query = query.filter_by(status=status)
    else:
        query = query.filter(Billing.status.in_(['pending', 'lunas']))

    billing_list = query.order_by(Billing.tanggal.desc()).all()

    return render_template('kasir/index.html',
                         billing_list=billing_list,
                         status=status)

@kasir_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        layanan = request.form.get('layanan')
        item_id = request.form.get('item_id')

        # Get layanan details and calculate total
        total = 0
        deskripsi_list = []

        if layanan == 'rawat_jalan':
            rj = RawatJalan.query.get(item_id)
            if rj:
                total = 50000  # Biaya admin rawat jalan
                deskripsi_list.append(f'Rawat Jalan - {rj.poliklinik.nama if rj.poliklinik else "Poli"}')

        elif layanan == 'rawat_inap':
            ri = RawatInap.query.get(item_id)
            if ri:
                # Calculate days and room cost
                days = (datetime.now() - ri.tanggal_masuk).days + 1
                total = float(ri.kamar.tarif) * days
                deskripsi_list.append(f'Rawat Inap - {ri.kamar.nama} ({days} hari)')

        elif layanan == 'resep':
            resep = Resep.query.get(item_id)
            if resep:
                for detail in resep.details:
                    total += float(detail.obat.harga) * detail.jumlah
                    deskripsi_list.append(f'Obat: {detail.obat.nama} x{detail.jumlah}')
                # Mark resep as selesai
                resep.status = 'selesai'

        elif layanan == 'laboratorium':
            lab = PemeriksaanLab.query.get(item_id)
            if lab:
                for detail in lab.details:
                    total += float(detail.jenis_pemeriksaan.harga)
                    deskripsi_list.append(f'Lab: {detail.jenis_pemeriksaan.nama}')
                lab.status = 'selesai'

        # Create billing
        billing = Billing(
            pasien_id=pasien_id,
            nomor_invoice=generate_invoice(),
            total=total,
            status='pending'
        )
        db.session.add(billing)
        db.session.flush()

        # Create billing detail
        detail = BillingDetail(
            billing_id=billing.id,
            layanan=layanan,
            item_id=item_id,
            deskripsi='\n'.join(deskripsi_list),
            jumlah=1,
            harga=total,
            total_harga=total
        )
        db.session.add(detail)
        db.session.commit()

        flash(f'Invoice {billing.nomor_invoice} berhasil dibuat!', 'success')
        return redirect(url_for('kasir.detail', id=billing.id))

    pasien_list = Pasien.query.filter_by(aktif=True).all()

    # Get pending layanan
    rawat_jalan = RawatJalan.query.filter_by(status='selesai').all()
    rawat_inap = RawatInap.query.filter_by(status='aktif').all()
    resep = Resep.query.filter_by(status='selesai').all()
    laboratorium = PemeriksaanLab.query.filter_by(status='selesai').all()

    return render_template('kasir/baru.html',
                         pasien_list=pasien_list,
                         rawat_jalan=rawat_jalan,
                         rawat_inap=rawat_inap,
                         resep=resep,
                         laboratorium=laboratorium)

@kasir_bp.route('/<int:id>')
@login_required
def detail(id):
    billing = Billing.query.get_or_404(id)
    return render_template('kasir/detail.html', billing=billing)

@kasir_bp.route('/<int:id>/bayar', methods=['GET', 'POST'])
@login_required
def bayarkan(id):
    billing = Billing.query.get_or_404(id)

    if request.method == 'POST':
        jumlah_bayar = float(request.form.get('jumlah_bayar'))
        metode = request.form.get('metode')

        # Create pembayaran
        pembayaran = Pembayaran(
            billing_id=billing.id,
            jumlah_bayar=jumlah_bayar,
            metode=metode,
            status='sukses'
        )
        db.session.add(pembayaran)

        billing.status = 'lunas'
        billing.metode_pembayaran = metode

        db.session.commit()
        flash('Pembayaran berhasil!', 'success')
        return redirect(url_for('kasir.detail', id=billing.id))

    return render_template('kasir/bayar.html', billing=billing)

@kasir_bp.route('/<int:id>/batal')
@login_required
def batal(id):
    billing = Billing.query.get_or_404(id)
    billing.status = 'batal'
    db.session.commit()
    flash('Invoice dibatalkan!', 'success')
    return redirect(url_for('kasir.index'))

@kasir_bp.route('/cari-pasien')
@login_required
def cari_pasien():
    """API untuk mencari tagihan pasien"""
    search = request.args.get('q', '')
    pasien = Pasien.query.filter(
        (Pasien.nik.like(f'%{search}%')) |
        (Pasien.nama_lengkap.like(f'%{search}%'))
    ).filter_by(aktif=True).limit(10).all()

    results = []
    for p in pasien:
        # Check if has pending billing
        pending = Billing.query.filter_by(pasien_id=p.id, status='pending').first()
        results.append({
            'id': p.id,
            'nik': p.nik,
            'nama': p.nama_lengkap,
            'has_pending': pending is not None
        })

    return {'results': results}
