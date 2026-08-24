from flask import Blueprint, request, jsonify, abort, g
from pydantic import ValidationError
from ..database import get_db
from .. import models, schemas, utils

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route("/", methods=["POST"])
def create_user():
    db = get_db()
    try:
        user_data = schemas.UserCreate(**request.get_json())
    except ValidationError as e:
        abort(422, description=e.errors())
        
    # Password hash
    hashed_pwd = utils.hash(user_data.password)
    user_data.password = hashed_pwd

    new_user = models.User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return jsonify(schemas.UserOut.model_validate(new_user, from_attributes=True).model_dump()), 201

@bp.route("/", methods=["GET"])
def get_users():
    db = get_db()
    users = db.query(models.User).all()
    return jsonify([schemas.UserOut.model_validate(u, from_attributes=True).model_dump() for u in users])

@bp.route("/<int:id>", methods=["GET"])
def get_user(id):
    db = get_db()
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
            abort(404, description=f"user with id: {id} was not found")
    return jsonify(schemas.UserOut.model_validate(user, from_attributes=True).model_dump())

@bp.route("/<int:id>", methods=["DELETE"])
def delete_user(id):
    db = get_db()
    a = db.query(models.User).filter(models.User.id == id)
    if a.first() == None:
        abort(404, description=f"user with id:{id} doesn't exist")
    a.delete(synchronize_session = False)
    db.commit()
    return '', 204

@bp.route("/<int:id>", methods=["PUT"])
def update_user(id):
    db = get_db()
    try:
        updated_post = schemas.UserCreate(**request.get_json())
    except ValidationError as e:
        abort(422, description=e.errors())
        
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user == None:
        abort(404, description=f"user with id: {id} was not found")

    hashed_pwd = utils.hash(updated_post.password)
    updated_post.password = hashed_pwd

    user_query.update(updated_post.model_dump(), synchronize_session = False)
    db.commit()
    return jsonify(schemas.UserOut.model_validate(user_query.first(), from_attributes=True).model_dump())