from flask import Blueprint, current_app, render_template
from sqlalchemy import select
from app.models import Image, Tag, Focus
from app import db

manager = Blueprint("manager", __name__)


@manager.route("/manager/<id>")
def tag_manager(id):
    image = db.session.scalar(select(Image).where(Image.id == id))
    b64full = image.get_fullsize_image_data_base64(current_app.config["IMAGE_PATH"])
    b64thumb = image.get_thumbnail_image_data_base64(current_app.config["IMAGE_PATH"])
    focus = Focus(image)
    return render_template(
        "manager.html",
        imdata=b64full,
        thumbdata=b64thumb,
        focus=focus,
        image=image,
        title="Manager",
    )


@manager.route("/gallery")
def show_gallery():
    return render_template("gallery.html")
