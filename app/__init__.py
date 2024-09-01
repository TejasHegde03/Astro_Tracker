from flask import Flask

import mysql.connector

def create_app():
    app = Flask(__name__)
    app.secret_key = '12345'  

    app.config['DB_HOST'] = 'localhost'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = '12345'
    app.config['DB_NAME'] = 'dbms_project'

    try:
        app.config['DB_CONNECTION'] = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        print("Connected to database successfully!")
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")

    # Register routes blueprint
    from .routes import routes_bp
    app.register_blueprint(routes_bp)

    return app
