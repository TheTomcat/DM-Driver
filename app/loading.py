from flask import Blueprint, current_app, render_template, request
from sqlalchemy import select
from app.models import Image, Message, Session, Focus
from app import db

loading = Blueprint("loading", __name__)


@loading.route("/loading")
def loading_page():
    if session_id := request.args.get("session"):
        s = select(Session).where(Session.id == session_id)
        session = db.session.scalar(s)
        image = session.image
        message = session.message
    else:
        if image_id := request.args.get("image"):
            q = select(Image).where(Image.id == image_id)
        else:
            q = Image.get_random()
        if message_id := request.args.get("message"):
            m = select(Message).where(Message.id == message_id)
        else:
            m = Message.get_random()
        image = db.session.scalar(q)
        message = db.session.scalar(m)
    imdata = image.get_fullsize_image_data_base64(current_app.config["IMAGE_PATH"])
    focus = Focus(image)
    return render_template(
        "loading.html.j2",
        imdata=imdata,
        message=message,
        focus=focus,
        title="Loading",
    )


@loading.route("/backdrop")
def backdrop_page():
    if session_id := request.args.get("session"):
        s = select(Session).where(Session.id == session_id)
        session = db.session.scalar(s)
        image = session.image
    else:
        if image_id := request.args.get("image"):
            q = select(Image).where(Image.id == image_id)
        else:
            q = Image.get_random()
        image = db.session.scalar(q)
    imdata = image.get_fullsize_image_data_base64(current_app.config["IMAGE_PATH"])
    focus = Focus(image)
    # Sendign the b64 data makes the page load smoother
    # The background is important (vs other websites where the background is incidental)
    # Having a dark background for a few seconds doesn't look as good
    return render_template(
        "backdrop.html.j2", imdata=imdata, focus=focus, title="Backdrop"
    )
