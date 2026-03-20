from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Billing, Pembayaran, Resep, PemeriksaanLab
from datetime import datetime
from sqlalchemy import func

keuangan_bp = Blueprint('keuangan', __name__, url_prefix='/keuangan')

@keuangan_bp.route('/')
@login_required
def index():
    return render_template('keuangan/index.html')

@keuangan_bp.route('/laporan')
@login_required
def laporan():
    # Get date filter
    tanggal_awal = request.args.get('tanggal_awal')
    tanggal_akhir = request.args.get('tanggal_akhir')

    if not tanggal_awal:
        tanggal_awal = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not tanggal_akhir:
        tanggal_akhir = datetime.now().strftime('%Y-%m-%d')

    # Get payments in date range
    pembayaran = Pembayaran.query.join(Billing).filter(
        Billing.status == 'lunas',
        func.date(Pembayaran.tanggal) >= tanggal_awal,
        func.date(Pembayaran.tanggal) <= tanggal_akhir
    ).all()

    total_pendapatan = sum(float(p.jumlah_bayar) for p in pembayaran)

    # Get summary by layanan
    summary_by_layanan = {}
    for p in pembayaran:
        for detail in p.billing.details:
            layanan = detail.layanan
            if layanan not in summary_by_layanan:
                summary_by_layanan[layanan] = 0
            summary_by_layanan[layanan] += float(detail.total_harga)

    # Get summary by payment method
    summary_by_metode = {}
    for p in pembayaran:
        metode = p.metode or 'Lainnya'
        if metode not in summary_by_metode:
            summary_by_metode[metode] = 0
        summary_by_metode[metode] += float(p.jumlah_bayar)

    return render_template('keuangan/laporan.html',
                         pembayaran=pembayaran,
                         total_pendapatan=total_pendapatan,
                         summary_by_layanan=summary_by_layanan,
                         summary_by_metode=summary_by_metode,
                         tanggal_awal=tanggal_awal,
                         tanggal_akhir=tanggal_akhir)

@keuangan_bp.route('/pendapatan')
@login_required
def pendapatan():
    # Monthly income for the last 12 months
    monthly_income = []
    for i in range(11, -1, -1):
        month_start = datetime.now().replace(day=1)
        from datetime import timedelta
        month_start = (month_start - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        total = db.session.query(func.sum(Pembayaran.jumlah_bayar)).join(Billing).filter(
            Billing.status == 'lunas',
            Pembayaran.tanggal >= month_start,
            Pembayaran.tanggal < month_end
        ).scalar() or 0

        monthly_income.append({
            'bulan': month_start.strftime('%b %Y'),
            'total': float(total)
        })

    return render_template('keuangan/pendapatan.html', monthly_income=monthly_income)

@keuangan_bp.route('/piutang')
@login_required
def piutang():
    """List pending/ unpaid bills"""
    pending_bills = Billing.query.filter_by(status='pending').order_by(Billing.tanggal.desc()).all()
    total_piutang = sum(float(b.total) for b in pending_bills)

    return render_template('keuangan/piutang.html',
                         pending_bills=pending_bills,
                         total_piutang=total_piutang)
