from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses sistem.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.pasien import pasien_bp
    from app.routes.rawat_jalan import rawat_jalan_bp
    from app.routes.rawat_inap import rawat_inap_bp
    from app.routes.igd import igd_bp
    from app.routes.rekam_medis import rekam_medis_bp
    from app.routes.farmasi import farmasi_bp
    from app.routes.laboratorium import laboratorium_bp
    from app.routes.kasir import kasir_bp
    from app.routes.keuangan import keuangan_bp
    from app.routes.gudang import gudang_bp
    from app.routes.koding import koding_bp
    from app.routes.bpjs import bpjs_bp
    from app.routes.laporan import laporan_bp
    from app.routes.jadwal import jadwal_bp
    from app.routes.radiologi import radiologi_bp
    from app.routes.bank_darah import bank_darah_bp
    from app.routes.ok import ok_bp
    from app.routes.vk import vk_bp
    from app.routes.bed_management import bed_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pasien_bp)
    app.register_blueprint(rawat_jalan_bp)
    app.register_blueprint(rawat_inap_bp)
    app.register_blueprint(igd_bp)
    app.register_blueprint(rekam_medis_bp)
    app.register_blueprint(farmasi_bp)
    app.register_blueprint(laboratorium_bp)
    app.register_blueprint(kasir_bp)
    app.register_blueprint(keuangan_bp)
    app.register_blueprint(gudang_bp)
    app.register_blueprint(koding_bp)
    app.register_blueprint(bpjs_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(jadwal_bp)
    app.register_blueprint(radiologi_bp)
    app.register_blueprint(bank_darah_bp)
    app.register_blueprint(ok_bp)
    app.register_blueprint(vk_bp)
    app.register_blueprint(bed_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
