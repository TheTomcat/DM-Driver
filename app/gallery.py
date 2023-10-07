from flask import Blueprint, current_app, render_template, request
from sqlalchemy import select, func
from app import db
from app.models import Tag, image_tags

gallery = Blueprint("gallery", __name__)


@gallery.route("/gallery")
def show_gallery():
    return render_template("gallery.html")


@gallery.route("/tags")
def get_all_tags():
    tags = select(Tag)
    all_tags = db.session.scalars(tags).all()
    return [{"tag": tag.tag, "id": tag.id} for tag in all_tags]


@gallery.route("/get")
def get_image_ids_by_tags():
    tags = [int(i) for i in request.args.get("tags").split(",")]
    if not tags or len(tags) == 0:
        return
    q = (
        select(image_tags.c.image_id, func.count(image_tags.c.image_id))
        .where(image_tags.c.tag_id.in_(tags))
        .group_by(image_tags.c.image_id)
    )
    return [{"image_id": o[0], "matches": o[1]} for o in db.session.execute(q).all()]
