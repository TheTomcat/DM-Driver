from app import create_app, db
from app.models import Image, Tag, Message, Directory

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "Image": Image,
        "Tag": Tag,
        "Message": Message,
        "Directory": Directory,
    }
