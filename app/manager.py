from flask import Blueprint, current_app, render_template, redirect, url_for
from sqlalchemy import select, func, text
from app.models import Image, Tag, Focus, image_tags
from app import db

manager = Blueprint("manager", __name__)


@manager.route("/manager")
def redirect_manager():
    q = (
        select(Image.id)
        .join(image_tags, image_tags.c.image_id == Image.id, isouter=True)
        .where(image_tags.c.tag_id == None)
        .order_by(Image.id)
        .limit(1)
    )
    next_id = db.session.scalar(q)
    return redirect(url_for("manager.tag_manager", id=next_id))


@manager.route("/manager/<id>")
def tag_manager(id):
    image = db.session.scalar(select(Image).where(Image.id == id))
    b64full = image.get_fullsize_image_data_base64()
    b64thumb = image.get_thumbnail_image_data_base64()
    focus = Focus(image)
    return render_template(
        "manager.html.j2",
        imdata=b64full,
        thumbdata=b64thumb,
        focus=focus,
        image=image,
        title="Manager",
    )


@manager.route("/gallery")
def show_gallery():
    return render_template("gallery.html.j2")


@manager.route("/messages")
def show_message():
    return render_template("messages.html.j2")


@manager.route("/sessions")
def show_sessions():
    return render_template("sessions.html.j2")
