from functools import partial
from flask import Blueprint, current_app
from flask.cli import with_appcontext
import glob
import click
import json
from pathlib import Path
from utils.thumbnail import parallel
from utils.dhash import im_hash
from sqlalchemy import select, delete
from app import db
from app.models import Image, Message, Entity
from PIL import Image as PImage

cli = Blueprint("cli", __name__)


def sprint(silent_flag, *args, **kwargs):
    "Hijack the print command, and suppress output if needed"
    if not silent_flag:
        print(*args, **kwargs)


def build_image_path(filename, as_thumbnail=False):
    basepath = Path(current_app.config["IMAGE_PATH"])
    thumbnail_dir = current_app.config["THUMBNAIL_SUBFOLDER"]
    if as_thumbnail:
        basepath = basepath.joinpath(thumbnail_dir)
    return basepath.joinpath(filename)


@cli.cli.command("parse-images")
@click.option("-s", "--silent", is_flag=True, default=False, help="Supress all output")
@click.option(
    "-r",
    "--regenerate-thumbnails",
    is_flag=True,
    default=False,
    help="Force regeneration of thumbnails",
)
@click.option(
    "-z",
    "--thumbnail-zoom",
    default=0.25,
    help="Zoom factor used to scale for thumbnails. Has no effect if not regenerating thumbnails",
)
@click.option(
    "-f",
    "--force_reparse",
    is_flag=True,
    default=False,
    help="Delete the database and rescan the folder",
)
def parse_images(silent, regenerate_thumbnails, thumbnail_zoom, force_reparse):
    images = glob.glob(current_app.config["IMAGE_PATH"] + "*.png")
    if regenerate_thumbnails:
        time, files = parallel(images, thumbnail_zoom)
        sprint(silent, f"[parse-image] Generated {len(files)} thumbnails in {time:.3}s")
    if force_reparse:
        db.session.execute(delete(Image))
        db.session.commit()
        sprint(silent, f"[parse-image] Cleared database of existing messages.")
    for image_path in images:
        filename = Path(image_path).name
        q = select(Image).where(Image.filename == filename)
        exists = db.session.execute(q).one_or_none()
        if exists is None:
            with PImage.open(image_path) as imdata:
                x, y = imdata.size
                # hash = im_hash(imdata) # Eventually we can use the hash to compare images
            image = Image(
                filename=filename, dimension_x=x, dimension_y=y, hash=hex(hash)
            )
            db.session.add(image)
            sprint(silent, f"[parse-image] Creating database entry for {filename}.")
        else:
            sprint(
                silent, f"[parse-image] Found database entry for {filename}, skipping"
            )
    db.session.commit()


@cli.cli.command("load-messages")
@click.option(
    "-m", "--message-file", help="The file containing messages. One per line."
)
@click.option(
    "-x",
    "--truncate-left",
    default=0,
    help="Remove the first 'x' characters from each line (e.g, for a bulleted list)",
)
@click.option(
    "-r",
    "--clear",
    is_flag=True,
    default=False,
    help="Remove all previous entries and load from a file afresh",
)
@click.option("-s", "--silent", is_flag=True, default=False, help="Supress all output")
def load_messages(message_file, truncate_left, clear, silent):
    if clear:
        db.session.execute(delete(Message))
        db.session.commit()
        sprint(silent, "[load-messages] Cleared database of existing messages")
    with open(message_file, "r") as f:
        lines = f.readlines()
    for line in lines:
        m = Message(message=line[truncate_left:])
        db.session.add(m)
    sprint(silent, f"[load-messages] Loaded {len(lines)} new messages.")
    db.session.commit()


@cli.cli.command("parse-compendium")
@click.option("-f", "--compendium_file", help="The filename of the compendium to parse")
@click.option("-s", "--silent", is_flag=True, default=False, help="Supress all output")
def parse_compendium(compendium_file, silent):
    if not compendium_file:
        return
    with open(compendium_file, "r") as f:
        data = json.load(f)
    for monster in data["monster"]:
        try:
            m = Entity(
                name=monster["name"],
                hit_dice=monster["hp"]["formula"],
                ac=find_max(monster, "ac"),
                cr=(
                    monster["cr"]
                    if isinstance(monster["cr"], str)
                    else monster["cr"]["cr"]
                ),
                initiative_modifier=monster["dex"],
                is_PC=False,
                source=monster["source"],
                source_page=monster["page"],
            )
        except Exception as e:
            print(monster)
            raise e
        sprint(silent, f"[parse-compendium] Parsing {monster['name']}")
        db.session.add(m)
    db.session.commit()


def find_max(data, index):
    def get_maximum_element_from_json(element):
        if isinstance(element, int):
            return element
        else:
            return element[index]

    return max(map(get_maximum_element_from_json, data[index]))
