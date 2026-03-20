from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import ICD10, ICD9, INACBGs

koding_bp = Blueprint('koding', __name__, url_prefix='/koding')

@koding_bp.route('/')
@login_required
def index():
    # Get all ICD-10 codes, paginated
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')

    query = ICD10.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (ICD10.kode.like(f'%{search}%')) |
            (ICD10.nama.like(f'%{search}%'))
        )

    if kategori:
        query = query.filter_by(kategori=kategori)

    pagination = query.order_by(ICD10.kode).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('koding/index.html',
                         icd10_list=pagination.items,
                         pagination=pagination,
                         search=search,
                         kategori=kategori)

@koding_bp.route('/search')
@login_required
def search():
    """API untuk pencarian ICD-10 (autocomplete)"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])

    results = ICD10.query.filter(
        ICD10.aktif == True,
        (ICD10.kode.like(f'%{q}%')) | (ICD10.nama.like(f'%{q}%'))
    ).limit(10).all()

    return jsonify([{
        'id': r.id,
        'kode': r.kode,
        'nama': r.nama,
        'kategori': r.kategori
    } for r in results])

@koding_bp.route('/api/<int:id>')
@login_required
def get_icd10(id):
    """API untuk mendapatkan detail ICD-10"""
    icd10 = ICD10.query.get_or_404(id)
    return jsonify({
        'id': icd10.id,
        'kode': icd10.kode,
        'nama': icd10.nama,
        'kategori': icd10.kategori
    })

# ==================== ICD-9 CM (TINDAKAN) ====================

@koding_bp.route('/icd9')
@login_required
def icd9_list():
    """Daftar kode ICD-9-CM"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')

    query = ICD9.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (ICD9.kode.like(f'%{search}%')) |
            (ICD9.nama.like(f'%{search}%'))
        )

    if kategori:
        query = query.filter_by(kategori=kategori)

    pagination = query.order_by(ICD9.kode).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('koding/icd9_list.html',
                         icd9_list=pagination.items,
                         pagination=pagination,
                         search=search,
                         kategori=kategori)

@koding_bp.route('/icd9/baru', methods=['GET', 'POST'])
@login_required
def icd9_baru():
    """Tambah kode ICD-9 baru"""
    if request.method == 'POST':
        kode = request.form.get('kode')
        nama = request.form.get('nama')
        kategori = request.form.get('kategori')

        # Cek duplikasi
        existing = ICD9.query.filter_by(kode=kode).first()
        if existing:
            flash('Kode ICD-9 sudah ada!', 'danger')
            return redirect(url_for('koding.icd9_baru'))

        icd9 = ICD9(
            kode=kode,
            nama=nama,
            kategori=kategori,
            aktif=True
        )

        db.session.add(icd9)
        db.session.commit()

        flash('Kode ICD-9 berhasil ditambahkan', 'success')
        return redirect(url_for('koding.icd9_list'))

    return render_template('koding/icd9_baru.html')

@koding_bp.route('/icd9/search')
@login_required
def icd9_search():
    """API pencarian ICD-9 (autocomplete)"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])

    results = ICD9.query.filter(
        ICD9.aktif == True,
        (ICD9.kode.like(f'%{q}%')) | (ICD9.nama.like(f'%{q}%'))
    ).limit(10).all()

    return jsonify([{
        'id': r.id,
        'kode': r.kode,
        'nama': r.nama,
        'kategori': r.kategori
    } for r in results])

@koding_bp.route('/icd9/api/<int:id>')
@login_required
def get_icd9(id):
    """API untuk mendapatkan detail ICD-9"""
    icd9 = ICD9.query.get_or_404(id)
    return jsonify({
        'id': icd9.id,
        'kode': icd9.kode,
        'nama': icd9.nama,
        'kategori': icd9.kategori
    })

# ==================== INA-CBGs ====================

@koding_bp.route('/inacbgs')
@login_required
def inacbgs_list():
    """Daftar kode INA-CBGs"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')

    query = INACBGs.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (INACBGs.kode_cbg.like(f'%{search}%')) |
            (INACBGs.nama_cbg.like(f'%{search}%'))
        )

    if kategori:
        query = query.filter_by(kategori=kategori)

    pagination = query.order_by(INACBGs.kode_cbg).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('koding/inacbgs_list.html',
                         inacbgs_list=pagination.items,
                         pagination=pagination,
                         search=search,
                         kategori=kategori)

@koding_bp.route('/inacbgs/baru', methods=['GET', 'POST'])
@login_required
def inacbgs_baru():
    """Tambah kode INA-CBGs baru"""
    if request.method == 'POST':
        kode_cbg = request.form.get('kode_cbg')
        nama_cbg = request.form.get('nama_cbg')
        tarif = request.form.get('tarif', 0)
        kategori = request.form.get('kategori')
        sub_kategori = request.form.get('sub_kategori')

        # Cek duplikasi
        existing = INACBGs.query.filter_by(kode_cbg=kode_cbg).first()
        if existing:
            flash('Kode INA-CBGs sudah ada!', 'danger')
            return redirect(url_for('koding.inacbgs_baru'))

        inacbgs = INACBGs(
            kode_cbg=kode_cbg,
            nama_cbg=nama_cbg,
            tarif=tarif or 0,
            kategori=kategori,
            sub_kategori=sub_kategori,
            aktif=True
        )

        db.session.add(inacbgs)
        db.session.commit()

        flash('Kode INA-CBGs berhasil ditambahkan', 'success')
        return redirect(url_for('koding.inacbgs_list'))

    return render_template('koding/inacbgs_baru.html')

@koding_bp.route('/inacbgs/api/search')
@login_required
def inacbgs_search():
    """API pencarian INA-CBGs (autocomplete)"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])

    results = INACBGs.query.filter(
        INACBGs.aktif == True,
        (INACBGs.kode_cbg.like(f'%{q}%')) | (INACBGs.nama_cbg.like(f'%{q}%'))
    ).limit(10).all()

    return jsonify([{
        'id': r.id,
        'kode_cbg': r.kode_cbg,
        'nama_cbg': r.nama_cbg,
        'tarif': float(r.tarif) if r.tarif else 0,
        'kategori': r.kategori
    } for r in results])

@koding_bp.route('/inacbgs/api/<int:id>')
@login_required
def get_inacbgs(id):
    """API untuk mendapatkan detail INA-CBGs"""
    inacbgs = INACBGs.query.get_or_404(id)
    return jsonify({
        'id': inacbgs.id,
        'kode_cbg': inacbgs.kode_cbg,
        'nama_cbg': inacbgs.nama_cbg,
        'tarif': float(inacbgs.tarif) if inacbgs.tarif else 0,
        'kategori': inacbgs.kategori,
        'sub_kategori': inacbgs.sub_kategori
    })