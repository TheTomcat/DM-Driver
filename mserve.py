from app import create_app, db
from app.models import Image, Tag, Message, Directory, Participant, Entity, Combat

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "Image": Image,
        "Tag": Tag,
        "Message": Message,
        "Directory": Directory,
        "Participant": Participant,
        "Entity": Entity,
        "Combat": Combat,
    }
