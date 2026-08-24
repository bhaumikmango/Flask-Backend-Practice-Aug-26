from flask import Blueprint, request, jsonify, abort, g
from pydantic import ValidationError
from ..database import get_db
from .. import models, schemas, oauth2

bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route("/", methods=["GET"])
@oauth2.require_user
def get_posts():
    db = get_db()
    posts = db.query(models.Post).all()
    return jsonify([schemas.Post.model_validate(p, from_attributes=True).model_dump() for p in posts])

@bp.route("/latest", methods=["GET"])
@oauth2.require_user
def get_latest_post():
    db = get_db()
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    if not post:
        abort(404, description="No posts found")
    return jsonify(schemas.Post.model_validate(post, from_attributes=True).model_dump())

@bp.route("/", methods=["POST"])
@oauth2.require_user
def create_posts():
    db = get_db()
    try:
        post_data = schemas.PostCreate(**request.get_json())
    except ValidationError as e:
        abort(422, description=e.errors())
        
    new_post = models.Post(**post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return jsonify(schemas.Post.model_validate(new_post, from_attributes=True).model_dump()), 201

@bp.route("/<int:id>", methods=["GET"])
@oauth2.require_user
def get_post(id):
    db = get_db()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
            abort(404, description=f"post with id: {id} was not found")
    return jsonify(schemas.Post.model_validate(post, from_attributes=True).model_dump())
    
@bp.route("/<int:id>", methods=["DELETE"])
@oauth2.require_user
def delete_post(id):
    db = get_db()
    a = db.query(models.Post).filter(models.Post.id == id)
    if a.first() == None:
        abort(404, description=f"post with id:{id} doesn't exist")
    a.delete(synchronize_session = False)
    db.commit()
    return '', 204

@bp.route("/<int:id>", methods=["PUT"])
@oauth2.require_user
def update_post(id):
    db = get_db()
    try:
        updated_post = schemas.PostCreate(**request.get_json())
    except ValidationError as e:
        abort(422, description=e.errors())
        
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        abort(404, description=f"post with id: {id} was not found")

    post_query.update(updated_post.model_dump(), synchronize_session = False)
    db.commit()
    return jsonify(schemas.Post.model_validate(post_query.first(), from_attributes=True).model_dump())
