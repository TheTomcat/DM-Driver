from flask import Blueprint, current_app, render_template, request, send_file
from sqlalchemy import select, func, text
from app.models import (
    Combat,
    Entity,
    Image,
    Participant,
    Tag,
    Message,
    calculate_thumbnail_size,
    image_tags,
    Session,
)
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


@api.post("/tags")
def create_tag():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    tag_data = request.json
    try:
        title = tag_data.get("tag")
        tag = db.session.scalar(select(Tag).where(Tag.tag == title.lower()))
        if not tag:
            tag = Tag(tag=title.lower())
            db.session.add(tag)
            db.session.commit()

            return build_success(tag.to_json())
        else:
            return fail(401, "Tag already exists")
    except Exception as e:
        return fail(400, "An error occured {e}")


@api.get("/image/<image_id>/tag")
def get_tags_of_image(image_id):
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tags = [tag.to_json() for tag in image.tags]
    return build_success(tags)


@api.put("/image/<image_id>/tag/<tag_id>")
def add_tag_id_to_image(image_id, tag_id):
    image = db.session.scalar(Image.get(image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tag = db.session.scalar(Tag.get(tag_id))
    if not tag:
        return fail(404, f"<Tag {tag_id} not found")
    if tag in image.tags:
        return fail(405, f'<Image {image_id}> already tagged with <Tag {tag_id}>"')
    image.tags.append(tag)
    db.session.add(tag)
    db.session.commit()
    return build_success(image.to_json())


@api.delete("/image/<image_id>/tag/<tag_id>")
def remove_tag_id_from_image(image_id, tag_id):
    image = db.session.scalar(Image.get(image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    tag = db.session.scalar(Tag.get(tag_id))
    if not tag:
        return fail(404, f"<Tag {tag_id} not found")
    if tag not in image.tags:
        return fail(405, f'<Image {image_id}> not tagged with <Tag {tag_id}>"')
    image.tags.remove(tag)
    db.session.commit()
    return build_success(image.to_json())


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
    try:
        with PImage.open(image.path) as image_data:
            image_io = BytesIO()
            image_data.save(image_io, "png")
            image_io.seek(0)
        return send_file(image_io, mimetype="image/png", download_name=image.filename)
    except FileNotFoundError:
        return fail(404, f"<Image {image_id}> not found")
    except Exception as e:
        return fail(400, f"Unknown error {e}")


@api.get("/image/<image_id>/thumb")
def get_thumbnail_image(image_id):
    args = {
        key: float(request.args.get(key))
        for key in ["width", "height", "scale"]
        if request.args.get(key)
    }
    if not args:
        args = {"width": 300}
    image = db.session.scalar(select(Image).where(Image.id == image_id))
    if not image:
        return fail(404, f"<Image {image_id}> not found")
    try:
        with PImage.open(image.path) as im:
            x, y = calculate_thumbnail_size((image.dimension_x, image.dimension_y), **args)

            im.thumbnail((x, y))

            image_io = BytesIO()
            im.save(image_io, "png")
            image_io.seek(0)
        return send_file(image_io, mimetype="image/png", download_name="t" + image.filename)
    except FileNotFoundError:
        return fail(404, f"<Image {image_id}> not found")
    except Exception as e:
        return fail(400, f"Unknown error {e}")

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


@api.get("/combat/<combat_id>")
def get_combat_by_id(combat_id):
    combat = db.session.scalar(select(Combat).where(Combat.id == combat_id))
    if not combat:
        return fail(404, f"Combat {combat_id} not found.")
    return build_success(combat.to_json())


@api.get("/combat")
def get_all_combats():
    combats = db.session.scalars(select(Combat)).all()
    # if not combats:
    #     return fail(404, f"Combats not found.")
    return build_success([combat.to_json() for combat in combats])


@api.post("/combat")
def create_new_combat():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    combat = request.json
    try:
        title = combat.get("title")
        c = Combat(title=title)
        db.session.add(c)
        db.session.commit()
        return build_success(c.to_json())
    except IndexError as e:
        return fail(401, "Invalid request, please supply {title:'title'}")


@api.put("/combat/participant")
def add_participant():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    participant = request.json
    if not isinstance(participant, dict):
        return fail(401, "Invalid request")
    try:
        print(participant)
        p = Participant(**participant)
        db.session.add(p)
        db.session.commit()
        return build_success(p.to_json())
    except Exception as e:
        return fail(400, f"An error occurred: {e}")


@api.delete("/combat/participant")
def remove_participant():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    participant = request.json
    if not isinstance(participant, dict) and "participant_id" not in participant:
        return fail(401, "Invalid request")
    try:
        participant = db.session.scalar(
            Participant.get(participant.get("participant_id"))
        )
        db.session.delete(participant)
        db.session.commit()
        return build_success()
    except Exception as e:
        return fail(400, f"An error occured {e}")


@api.patch("/combat/participant")
def modify_participant():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    participant_data = request.json
    if (
        not isinstance(participant_data, dict)
        and "participant_id" not in participant_data
    ):
        return fail(401, "Invalid request")
    try:
        participant = db.session.scalar(
            Participant.get(participant_data.get("participant_id"))
        )
        for key, val in participant_data.items():
            if key == "participant_id":
                continue
            if key == "conditions":
                val = ",".join(val)
            setattr(participant, key, val)
        db.session.commit()
        return build_success(participant.to_json())
    except Exception as e:
        return fail(400, f"An error occured {e}")


@api.get("/participant/<participant_id>")
def get_participant_by_id(participant_id):
    participant = db.session.scalar(
        select(Participant).where(Participant.id == participant_id)
    )
    if not participant:
        return fail(404, f"Participant {participant_id} not found.")
    return build_success(participant.to_json())


@api.get("/participant")
def get_all_participants():
    participants = db.session.scalars(select(Participant)).all()
    # if not participants:
    #     return fail(404, f"Participants not found.")
    return build_success([participant.to_json() for participant in participants])


@api.get("/entity/<entity_id>")
def get_entity_by_id(entity_id):
    entity = db.session.scalar(select(Entity).where(Entity.id == entity_id))
    if not entity:
        return fail(404, f"Entity {entity_id} not found.")
    return build_success(entity.to_json())


@api.get("/entity")
def get_all_entities():
    entities = db.session.scalars(select(Entity)).all()
    # if not entities:
    #     return fail(404, f"entities not found.")
    return build_success([entity.to_json() for entity in entities])


@api.put("/entity")
def add_entity():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    entity = request.json
    if not isinstance(entity, dict):
        return fail(401, "Invalid request")
    try:
        # print(entity)
        e = Entity(**entity)
        db.session.add(e)
        db.session.commit()
        return build_success(e.to_json())
    except Exception as error:
        return fail(400, f"An error occurred: {error}")
    

@api.patch("/entity")
def modify_entity():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return fail(415, "Invalid request, unsupported Content-Type")
    entity_data = request.json
    if (
        not isinstance(entity_data, dict)
        and "entity_id" not in entity_data
    ):
        return fail(401, "Invalid request")
    try:
        entity = db.session.scalar(
            Entity.get(entity_data.get("entity_id"))
        )
        for key, val in entity_data.items():
            if key == "entity_id":
                continue
            setattr(entity, key, val)
        db.session.commit()
        return build_success(entity.to_json())
    except Exception as e:
        return fail(400, f"An error occured {e}")