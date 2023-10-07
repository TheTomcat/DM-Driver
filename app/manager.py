from flask import Blueprint, current_app, render_template
from sqlalchemy import select
from app.models import Image, Tag, Focus
from app import db

manager = Blueprint('manager', __name__)

@manager.route('/manager/<id>')
def tag_manager(id):
    image = db.session.scalar(select(Image).where(Image.id == id))
    b64full = image.get_fullsize_image_data_base64(current_app.config['IMAGE_PATH'])
    b64thumb = image.get_thumbnail_image_data_base64(current_app.config['IMAGE_PATH'])
    focus = Focus(image)
    return render_template('manager.html', imdata=b64full, thumbdata=b64thumb, focus=focus, image=image, title="Manager")


@manager.post('/manager/<id>/tags/<tag_name>')
def add_tag(id, tag_name):
    image = db.session.scalar(select(Image).where(Image.id == id))
    if not image:
        return 404
    tag = db.session.scalar(select(Tag).where(Tag.tag == tag_name.lower()))
    if not tag:
        tag = Tag(tag=tag_name.lower())
    if tag in image.tags:
        return 'Already exists'
    image.tags.append(tag)
    db.session.add(tag)
    db.session.commit()
    return 'OK'

@manager.get('/manager/<id>/tags')
def get_tags(id):
    image = db.session.scalar(select(Image).where(Image.id == id))
    if not image:
        return 404
    tags = [tag.tag for tag in image.tags]
    return tags

@manager.delete('/manager/<id>/tags/<tag_name>')
def remove_tag(id, tag_name):
    image = db.session.scalar(select(Image).where(Image.id == id))
    if not image:
        return 404
    tag = db.session.scalar(select(Tag).where(Tag.tag == tag_name.lower()))
    if not tag:
        return 401
    if tag not in image.tags:
        return 401
    image.tags.remove(tag)
    db.session.commit()
    return 'OK'

