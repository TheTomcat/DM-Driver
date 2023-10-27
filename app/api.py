from flask import Blueprint, current_app, render_template, request, send_file
from sqlalchemy import select, func, text
from app.models import Image, Tag, Message, image_tags, Session
from io import BytesIO
from PIL import Image as PImage
from app import db

api = Blueprint("api", __name__)


def build_success(data=None):
    if data:
        return {"response": "OK", "payload": data}
    return {"response": "OK"}


def fail(error_code, error_message):
    return {
        "response": "Fail",
        "error_code": error_code,
        "error_message": error_message,
    }


@api.get("/tags")
def get_all_tags():
    tags = select(Tag)
    all_tags = db.session.scalars(tags).all()
    # return build_success([{"tag": tag.tag, "id": tag.id} for tag in all_tags])
    return build_success([tag.to_json() for tag in all_tags])


@api.get("/image/<image_id>/tag")
def get_tags_of_image(image_id):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tags = [tag.to_json() for tag in image.tags]
    return build_success(tags)


@api.post("/image/<image_id>/tag/<tag_name>")
def add_tag_to_image(image_id: int, tag_name: str):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tag = db.session.scalar(select(Tag).where(Tag.tag == tag_name.lower()))
    if not tag:
        tag = Tag(tag=tag_name.lower())
    if tag in image.tags:
        return fail(405, f'<Image {image_id}> already tagged with "{tag_name}"')
    image.tags.append(tag)
    db.session.add(tag)
    db.session.commit()
    return build_success(image.to_json())


@api.delete("/image/<image_id>/tag/<tag_name>")
def remove_tag_from_image(image_id, tag_name):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tag = db.session.scalar(select(Tag).where(Tag.tag == tag_name.lower()))
    if not tag:
        return fail(404, f"<Tag {tag_name}> does not exist.")
    if tag not in image.tags:
        return fail(
            405, f'<Image {image_id} not tagged with "{tag_name}" - cannot remove'
        )
    image.tags.remove(tag)
    db.session.commit()
    return build_success(image.to_json())


@api.get("/image/random")
def get_random_image():
    image = db.session.scalar(Image.get_random())
    return build_success(image.to_json())


@api.get("/message/<message_id>")
def get_message_by_id(message_id):
    message = db.session.scalar(select(Message).where(Message.id == message_id))
    if not message:
        return fail(404, f"<Message {message_id}> not found")
    return build_success(message.to_json())


@api.get("/message")
def get_all_messages():
    all_messages = db.session.scalars(select(Message)).all()
    if not all_messages:
        return fail(404, f"Unknown error")
    return build_success([message.to_json() for message in all_messages])


@api.get("/message/random")
def get_random_message():
    message = db.session.scalar(Message.get_random())
    return build_success(message.to_json())


@api.post("/message")
def new_message():
    data = request.json
    print(data)
    msg = data.get("message")
    if not msg:
        return fail(401, "Invalid request")
    message = Message(message=msg)
    db.session.add(message)
    db.session.commit()
    return build_success(message.to_json())


@api.get("/image/<image_id>")
def get_image_by_id(image_id):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    return build_success(image.to_json())


@api.get("/image/<image_id>/full")
def get_fullsize_image(image_id):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    image_data = PImage.open(current_app.config["IMAGE_PATH"] + image.filename)
    image_io = BytesIO()
    image_data.save(image_io, "png")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png", download_name=image.filename)


@api.get("/image/<image_id>/thumb")
def get_thumbnail_image(image_id):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    image_data = PImage.open(
        current_app.config["IMAGE_PATH"] + "thumbnails\\" + image.filename
    )
    image_io = BytesIO()
    image_data.save(image_io, "png")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png", download_name="t" + image.filename)


@api.get("/image")
def get_images_by_best_tag_match():
    try:
        tags = [int(i) for i in request.args.get("tags").split(",")]
        if not tags or len(tags) == 0:
            raise ValueError
    except:
        return fail(400, f"Invalid tag list")
    # print(tags)
    q = (
        select(
            image_tags.c.image_id,
            func.count(image_tags.c.image_id).label("match"),
            func.aggregate_strings(image_tags.c.tag_id, ",").label("tags"),
        )
        .where(image_tags.c.tag_id.in_(tags))
        .group_by(image_tags.c.image_id)
        .order_by(text("match DESC"))
        .limit(12)
    )
    return build_success(
        {
            "tag_list": tags,
            "images": [
                {
                    "image_id": o[0],
                    "matches": o[1],
                    "tags": [int(i) for i in o[2].split(",")],
                }
                for o in db.session.execute(q).all()
            ],
        }
    )


@api.post("/image/<image_id>/focus")
def set_image_focal_point(image_id):
    try:
        fx = float(request.args.get("x", None))
        fy = float(request.args.get("y", None))
    except ValueError:
        return fail(401, "Invalid focal point")
    if not (0 <= fx <= 1) and (0 <= fy <= 1):
        return fail(401, "Invalid focal point")
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    image.focus_x = int(fx * image.dimension_x)
    image.focus_y = int(fy * image.dimension_y)
    db.session.commit()
    return build_success(image.to_json())


@api.get("/session/<session_id>")
def get_session_by_id(session_id):
    session = db.session.scalar(select(Session).where(Session.id == session_id))
    if not session:
        return fail(404, f"Session {session_id} not found.")
    return build_success(session.to_json())


@api.post("/session")  # TODO: Allow sessions to have empty values (for random)
def create_session():
    try:
        image_id = int(request.args.get("image"))
        message_id = int(request.args.get("message"))
    except:
        return fail(401, "Invalid request")
    s = Session(image_id=image_id, message_id=message_id)
    db.session.add(s)
    db.session.commit()
    return s.to_json()


@api.get("/session")
def get_all_sessions():
    sessions = select(Session)
    all_sessions = db.session.scalars(sessions).all()
    return build_success([session.to_json() for session in all_sessions])
