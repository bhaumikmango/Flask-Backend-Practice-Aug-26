from flask import Blueprint, request, jsonify, abort
from .. import database, schemas, models, utils, oauth2

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    db = database.get_db()
    
    # OAuth2PasswordRequestForm uses form data
    username = request.form.get('username')
    password = request.form.get('password')

    user = db.query(models.User).filter(models.User.email == username).first()

    if not user:
        abort(404, description='Invalid Credentials')

    if not utils.verify_pass(password, user.password):
        abort(404, description='Invalid Credentials')

    # Create Access Token
    access_token = oauth2.create_access_token(data = {'user_id' : user.id})

    # Return Access Token
    return jsonify({'access_token' : access_token, 'token_type' : 'bearer'})
