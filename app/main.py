import os
import sys
sys.path.insert(0, '/opt/taskboard/bot')

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv('/opt/taskboard/.env')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'fallback_secret')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from routes import register_routes
register_routes(app, login_manager)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
