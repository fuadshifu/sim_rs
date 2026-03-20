from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app import db
from app.models import ICD10

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