from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


# ... other imports and configurations

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # ... other app configurations (secret key, database, etc.)

    # Hier definieren wir den login Endpoint ohne Blueprint
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # ... deine Login-Logik (z.B. Überprüfung von Benutzername und Passwort)
            # ... wenn Login erfolgreich:
            # login_user(user)
            # return redirect(url_for('dashboard')) # oder eine andere Zielseite
            # ... wenn Login fehlgeschlagen:
            # flash('Ungültige Anmeldedaten')

        return render_template('login.html')

    # ... other route definitions

    return app


# Wenn du Blueprints verwendest:
# main_bp = Blueprint("main", __name__, url_prefix="/", template_folder="templates") # Beispiel für einen 'main' Blueprint
# @main_bp.route("/login", methods=["GET", "POST"])
# def login():
    # ... (gleiche Login-Logik wie oben)
    # return render_template("login.html")
# app.register_blueprint(main_bp)

