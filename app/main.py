from flask import Flask, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas, utils
from .database import engine, close_db
from .routers import post, user, auth
from werkzeug.exceptions import HTTPException

models.Base.metadata.create_all(bind = engine)

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(post.bp)
app.register_blueprint(user.bp)
app.register_blueprint(auth.bp)

@app.route("/")
def index():
    return render_template("index.html")

# Teardown context for db
app.teardown_appcontext(close_db)

# Basic error handler for JSON responses
@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }).data
    response.content_type = "application/json"
    return response

while True:    
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', user = 'postgres', password = 'password123', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print('DB connection successful')
        break
    except Exception as e:
        print(e)
        time.sleep(2)