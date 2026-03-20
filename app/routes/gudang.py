from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import KategoriBarang, Barang, TransaksiStock
from datetime import datetime

gudang_bp = Blueprint('gudang', __name__, url_prefix='/gudang')

# ========== KATEGORI ==========
@gudang_bp.route('/kategori')
@login_required
def kategori():
    kategori_list = KategoriBarang.query.filter_by(aktif=True).order_by(KategoriBarang.nama).all()
    return render_template('gudang/kategori.html', kategori_list=kategori_list)

@gudang_bp.route('/kategori/baru', methods=['GET', 'POST'])
@login_required
def kategori_baru():
    if request.method == 'POST':
        kategori = KategoriBarang(
            nama=request.form.get('nama'),
            kode=request.form.get('kode')
        )
        db.session.add(kategori)
        db.session.commit()
        flash('Kategori berhasil ditambahkan!', 'success')
        return redirect(url_for('gudang.kategori'))
    return render_template('gudang/kategori_baru.html')

@gudang_bp.route('/kategori/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def kategori_edit(id):
    kategori = KategoriBarang.query.get_or_404(id)
    if request.method == 'POST':
        kategori.nama = request.form.get('nama')
        kategori.kode = request.form.get('kode')
        db.session.commit()
        flash('Kategori berhasil diperbarui!', 'success')
        return redirect(url_for('gudang.kategori'))
    return render_template('gudang/kategori_edit.html', kategori=kategori)

# ========== BARANG ==========
@gudang_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    kategori_id = request.args.get('kategori_id', '')

    query = Barang.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (Barang.nama.like(f'%{search}%')) |
            (Barang.kode.like(f'%{search}%'))
        )
    if kategori_id:
        query = query.filter_by(kategori_id=kategori_id)

    barang_list = query.order_by(Barang.nama).all()
    kategori_list = KategoriBarang.query.filter_by(aktif=True).all()

    return render_template('gudang/index.html',
                         barang_list=barang_list,
                         kategori_list=kategori_list,
                         search=search,
                         kategori_id=kategori_id)

@gudang_bp.route('/barang/baru', methods=['GET', 'POST'])
@login_required
def barang_baru():
    if request.method == 'POST':
        barang = Barang(
            nama=request.form.get('nama'),
            kode=request.form.get('kode'),
            kategori_id=request.form.get('kategori_id') or None,
            jenis=request.form.get('jenis'),
            stok=request.form.get('stok') or 0,
            stok_minimum=request.form.get('stok_minimum') or 10,
            satuan=request.form.get('satuan'),
            harga_satuan=request.form.get('harga_satuan') or 0
        )
        db.session.add(barang)
        db.session.commit()
        flash('Barang berhasil ditambahkan!', 'success')
        return redirect(url_for('gudang.index'))

    kategori_list = KategoriBarang.query.filter_by(aktif=True).all()
    return render_template('gudang/barang_baru.html', kategori_list=kategori_list)

@gudang_bp.route('/barang/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def barang_edit(id):
    barang = Barang.query.get_or_404(id)

    if request.method == 'POST':
        barang.nama = request.form.get('nama')
        barang.kode = request.form.get('kode')
        barang.kategori_id = request.form.get('kategori_id') or None
        barang.jenis = request.form.get('jenis')
        barang.stok_minimum = request.form.get('stok_minimum')
        barang.satuan = request.form.get('satuan')
        barang.harga_satuan = request.form.get('harga_satuan')
        db.session.commit()
        flash('Barang berhasil diperbarui!', 'success')
        return redirect(url_for('gudang.index'))

    kategori_list = KategoriBarang.query.filter_by(aktif=True).all()
    return render_template('gudang/barang_edit.html', barang=barang, kategori_list=kategori_list)

# ========== TRANSAKSI STOCK ==========
@gudang_bp.route('/transaksi')
@login_required
def transaksi():
    barang_id = request.args.get('barang_id', '')
    jenis = request.args.get('jenis', '')

    query = TransaksiStock.query

    if barang_id:
        query = query.filter_by(barang_id=barang_id)
    if jenis:
        query = query.filter_by(jenis=jenis)

    transaksi_list = query.order_by(TransaksiStock.tanggal.desc()).limit(100).all()
    barang_list = Barang.query.filter_by(aktif=True).all()

    return render_template('gudang/transaksi.html',
                         transaksi_list=transaksi_list,
                         barang_list=barang_list,
                         barang_id=barang_id,
                         jenis=jenis)

@gudang_bp.route('/transaksi/baru', methods=['GET', 'POST'])
@login_required
def transaksi_baru():
    if request.method == 'POST':
        barang_id = request.form.get('barang_id')
        jenis = request.form.get('jenis')
        jumlah = int(request.form.get('jumlah'))
        referensi = request.form.get('referensi')
        catatan = request.form.get('catatan')

        barang = Barang.query.get(barang_id)
        if not barang:
            flash('Barang tidak ditemukan!', 'danger')
            return redirect(url_for('gudang.transaksi_baru'))

        # Update stock
        if jenis == 'masuk':
            barang.stok += jumlah
        elif jenis == 'keluar':
            if barang.stok < jumlah:
                flash(f'Stok tidak cukup! Stok tersedia: {barang.stok}', 'danger')
                return redirect(url_for('gudang.transaksi_baru'))
            barang.stok -= jumlah

        # Create transaction
        trans = TransaksiStock(
            barang_id=barang_id,
            jenis=jenis,
            jumlah=jumlah,
            referensi=referensi,
            catatan=catatan,
            user_id=current_user.id
        )
        db.session.add(trans)
        db.session.commit()

        flash(f'Stok berhasil diperbarui! Stok baru: {barang.stok}', 'success')
        return redirect(url_for('gudang.transaksi'))

    barang_list = Barang.query.filter_by(aktif=True).all()
    return render_template('gudang/transaksi_baru.html', barang_list=barang_list)

@gudang_bp.route('/stok-rendah')
@login_required
def stok_rendah():
    barang_list = Barang.query.filter(
        Barang.stok <= Barang.stok_minimum,
        Barang.aktif == True
    ).order_by(Barang.stok).all()

    return render_template('gudang/stok_rendah.html', barang_list=barang_list)
