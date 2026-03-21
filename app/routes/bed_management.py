from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Kamar, TempatTidur, Pasien, RawatInap
from datetime import datetime, date
from sqlalchemy import func

bed_bp = Blueprint('bed', __name__, url_prefix='/bed')


@bed_bp.route('/')
@login_required
def index():
    """Dashboard bed availability - real time"""
    # Get all rooms with bed status
    kamar_list = Kamar.query.all()

    bed_summary = []
    for kamar in kamar_list:
        tempat_tidur = kamar.tempat_tidur
        total = len(tempat_tidur)
        tersedia = sum(1 for tt in tempat_tidur if tt.status == 'tersedia')
        occupied = sum(1 for tt in tempat_tidur if tt.status == 'occupied')
        maintenance = sum(1 for tt in tempat_tidur if tt.status == 'maintenance')

        # Calculate BOR
        if total > 0:
            bor = (occupied / total) * 100
        else:
            bor = 0

        bed_summary.append({
            'kamar': kamar,
            'total': total,
            'tersedia': tersedia,
            'occupied': occupied,
            'maintenance': maintenance,
            'bor': round(bor, 1)
        })

    # Overall stats
    total_beds = sum(b['total'] for b in bed_summary)
    total_tersedia = sum(b['tersedia'] for b in bed_summary)
    total_occupied = sum(b['occupied'] for b in bed_summary)
    overall_bor = (total_occupied / total_beds * 100) if total_beds > 0 else 0

    return render_template('bed/index.html',
                         bed_summary=bed_summary,
                         total_beds=total_beds,
                         total_tersedia=total_tersedia,
                         total_occupied=total_occupied,
                         overall_bor=round(overall_bor, 1))


@bed_bp.route('/available')
@login_required
def available():
    """JSON: bed tersedia per kelas"""
    kelas = request.args.get('kelas', '')

    query = db.session.query(
        Kamar.kelas,
        func.count(TempatTidur.id).label('total'),
        func.sum(db.case((TempatTidur.status == 'tersedia', 1), else_=0)).label('tersedia')
    ).join(TempatTidur).group_by(Kamar.kelas)

    if kelas:
        query = query.filter(Kamar.kelas == kelas)

    results = query.all()

    data = [{'kelas': r.kelas, 'total': r.total, 'tersedia': r.tersedia} for r in results]

    return jsonify(data)


@bed_bp.route('/occupancy')
@login_required
def occupancy():
    """Laporan tingkat hunian (BOR)"""
    # Get date range
    bulan = request.args.get('bulan', datetime.now().strftime('%Y-%m'))

    try:
        year, month = map(int, bulan.split('-'))
    except:
        year, month = datetime.now().year, datetime.now().month

    # Calculate BOR for the month
    # Simplified calculation - actual BOR needs more complex logic
    kamar_list = Kamar.query.all()

    report = []
    for kamar in kamar_list:
        tempat_tidur = kamar.tempat_tidur
        total_beds = len(tempat_tidur)
        if total_beds == 0:
            continue

        # Calculate available bed days
        days_in_month = 31  # Simplified
        available_days = total_beds * days_in_month

        # Get occupied days from rawat inap (simplified)
        occupied_days = 0  # This would need proper calculation

        bor = (occupied_days / available_days * 100) if available_days > 0 else 0

        report.append({
            'kelas': kamar.kelas,
            'total_beds': total_beds,
            'available_days': available_days,
            'occupied_days': occupied_days,
            'bor': round(bor, 1)
        })

    return render_template('bed/occupancy.html', report=report, bulan=bulan)


@bed_bp.route('/turnover')
@login_required
def turnover():
    """Laporan turnover tempat tidur"""
    # Get patients who were discharged recently
    start_date = request.args.get('start_date', (date.today()).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))

    discharged = RawatInap.query.filter(
        RawatInap.tgl_keluar >= start_date,
        RawatInap.tgl_keluar <= end_date
    ).all()

    turnover_count = len(discharged)

    return render_template('bed/turnover.html', discharged=discharged, turnover_count=turnover_count,
                         start_date=start_date, end_date=end_date)


@bed_bp.route('/assign', methods=['POST'])
@login_required
def assign():
    """Assign pasien ke bed (dari rawat inap)"""
    tempat_tidur_id = request.form.get('tempat_tidur_id')
    pasien_id = request.form.get('pasien_id')

    tt = TempatTidur.query.get(tempat_tidur_id)
    if not tt:
        flash('Tempat tidur tidak ditemukan', 'danger')
        return redirect(url_for('bed.index'))

    if tt.status != 'tersedia':
        flash('Tempat tidur tidak tersedia', 'danger')
        return redirect(url_for('bed.index'))

    # Update bed status
    tt.status = 'occupied'
    db.session.commit()

    flash(f'Pasien berhasil di-assign ke tempat tidur {tt.no_bed}', 'success')
    return redirect(url_for('bed.index'))


@bed_bp.route('/release', methods=['POST'])
@login_required
def release():
    """Release bed (pasien keluar)"""
    tempat_tidur_id = request.form.get('tempat_tidur_id')

    tt = TempatTidur.query.get(tempat_tidur_id)
    if not tt:
        flash('Tempat tidur tidak ditemukan', 'danger')
        return redirect(url_for('bed.index'))

    # Update bed status
    tt.status = 'tersedia'
    tt.pasien_id = None

    db.session.commit()
    flash(f'Tempat tidur {tt.no_bed} berhasil di-release', 'success')
    return redirect(url_for('bed.index'))


@bed_bp.route('/waiting')
@login_required
def waiting():
    """List pasien waiting untuk bed"""
    # Patients waiting for admission (simplified)
    # In real system, this would track waiting list
    waiting_list = []

    return render_template('bed/waiting.html', waiting_list=waiting_list)