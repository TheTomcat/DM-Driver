from app import db

from sqlalchemy import Column, Delete, String, Table, ForeignKey, select
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask import url_for
from typing_extensions import Annotated

import base64
import math
import random
from PIL import Image as PImage
from pathlib import Path

image_tags = Table(
    "image_tags",
    db.Model.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Selector(object):
    @classmethod
    def get_by_id_or_random(cls, id=None):
        if id is None:
            return cls.get_random()
        return select(cls).where(cls.id == id)

    @classmethod
    def get_random(cls):
        return select(cls).order_by(func.random())


def get_image_as_base64(path):
    with open(path, "rb") as image:
        data = base64.b64encode(image.read())
    return data.decode("ascii")


def get_image_thumbnail_as_base64(image: "Image", scale):
    """scale can be a single number - in which case, scale the image up or down by that fraction, or it can be a (width,height) tuple, in which case the image will be resized to fit within that bounding box"""
    if isinstance(scale, (int, float)):
        aspect_ratio = scale
    elif isinstance(scale, (tuple, list)):
        if len(scale) != 2:
            raise IndexError("Scale must be a number or an iterable of length 2")
        aspect_ratio = min(scale[0] / image.dimension_x, scale[1] / image.dimension_y)
    with open(image.path, "rb") as f:
        imdata = PImage.open(f)
        imdata.thumbnail(
            (
                int(aspect_ratio * image.dimension_x),
                int(aspect_ratio * image.dimension_y),
            )
        )
        output = base64.b64encode(imdata.tobytes())
        return output.decode("ascii")


class Image(db.Model, Selector):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    focus_x: Mapped[int] = mapped_column(nullable=True)
    focus_y: Mapped[int] = mapped_column(nullable=True)
    hash: Mapped[str] = mapped_column(String(20), index=True)
    dimension_x: Mapped[int]
    dimension_y: Mapped[int]
    tags: Mapped[list["Tag"]] = relationship(
        back_populates="images", secondary=image_tags
    )
    directory_id: Mapped[int] = mapped_column(ForeignKey("directories.id"))
    directory: Mapped["Directory"] = relationship(back_populates="images")

    def get_fullsize_image_data_base64(self, base_path=None):
        if base_path is not None:
            raise DeprecationWarning("BasePath should not be used")
        return get_image_as_base64(Path(self.directory.path, self.filename))

    def get_thumbnail_image_data_base64(self, base_path=None):
        if base_path is not None:
            raise DeprecationWarning("BasePath should not be used")
        # return get_image_as_base64(base_path + "thumbnails\\" + self.filename)
        return get_image_thumbnail_as_base64(self, (300, 300))

    @property
    def path(self):
        return Path(self.directory.path, self.filename)

    @property
    def url(self):
        return url_for("api.get_fullsize_image", image_id=self.id)

    @property
    def url_thumbnail(self):
        return url_for("api.get_thumbnail_image", image_id=self.id)

    def to_json(self):
        return {
            "image_id": self.id,
            "filename": self.filename,
            "dimensions": (self.dimension_x, self.dimension_y),
            "url": self.url,
            "thumbnail": self.url_thumbnail,
        }


class Directory(db.Model):
    __tablename__ = "directories"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    images: Mapped[list["Image"]] = relationship(back_populates="directory")


class Tag(db.Model):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30))
    images: Mapped[list["Image"]] = relationship(
        back_populates="tags", secondary=image_tags
    )

    def to_json(self):
        return {"tag_id": self.id, "tag": self.tag}


class Message(db.Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(400))

    @classmethod
    def get_random(cls):
        return select(cls).order_by(func.random())

    def to_json(self):
        return {"message_id": self.id, "message": self.message}


class Session(db.Model):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), insert_default="")
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
    image: Mapped["Image"] = relationship("Image")
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    message: Mapped["Message"] = relationship("Message")

    def to_json(self):
        return {
            "session_id": self.id,
            "title": self.title,
            "message_id": self.message_id,
            "image_id": self.image_id,
        }


class Focus:
    def __init__(self, image: Image, focus=None):
        self.image = image
        self.dx = image.dimension_x
        self.dy = image.dimension_y
        if focus:
            self.fx = focus[0]
            self.fy = focus[1]
        elif self.image.focus_x is not None:
            self.fx = self.image.focus_x
            self.fy = self.image.focus_y
        else:
            self.fx = -400 + self.dx / 2
            self.fy = self.dy / 2 - 400

    @property
    def params(self):
        return self.fx, self.fy, self.dx, self.dy

    @staticmethod
    def get_zoom(fx, fy, dx, dy):
        return 1 / (2 * min([fx / dx, fy / dy, (dx - fx) / dx, (dy - fy) / dy]))

    @property
    def zoom(self):
        return self.get_zoom(*self.params)  # self.fx, self.fy, self.dx, self.dy)

    @property
    def x(self):
        return self.fx - self.dx / 2

    @property
    def y(self):
        return self.dy / 2 - self.fy

    def wangle(self, angle) -> "Focus":
        r = min(self.image.dimension_x, self.image.dimension_y) / 4
        x = self.image.dimension_x / 2 + r * math.cos(angle) * random.random()
        y = self.image.dimension_y / 2 - r * math.sin(angle) * random.random()
        f = Focus(self.image)
        f.fx = x
        f.fy = y
        return (
            f  # x, y, self.get_zoom(x,y,self.image.dimension_x, self.image.dimension_y)
        )

    @property
    def csstransform(self) -> str:
        return (
            "@keyframes slowpan {"
            "0% {"
            f"   transform:translate3d({self.x}px,{self.y}px,0) scale({self.zoom});"
            "}"
            "50% {"
            f"   transform:translate3d(0,0,0) scale(1.1);"
            "}"
            "100% {"
            f"   transform:translate3d(400px,-200px,0) scale(1.5);"
            "}"
            "}"
        )
