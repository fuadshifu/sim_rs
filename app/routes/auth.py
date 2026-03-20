from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Role

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.aktif:
                flash('Akun Anda tidak aktif. Hubungi administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            flash(f'Selamat datang, {user.nama_lengkap}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nama_lengkap = request.form.get('nama_lengkap')
        nip = request.form.get('nip')
        role_id = request.form.get('role_id')

        # Validation
        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan.', 'danger')
            return render_template('auth/register.html')

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Default role adalah 'dokter' jika tidak dipilih
        if not role_id:
            role = Role.query.filter_by(name='dokter').first()
            role_id = role.id if role else 1

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            nama_lengkap=nama_lengkap,
            nip=nip,
            role_id=role_id,
            aktif=True
        )

        db.session.add(user)
        db.session.commit()

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    roles = Role.query.all()
    return render_template('auth/register.html', roles=roles)
