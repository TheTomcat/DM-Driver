import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def as_bool(value):
    if value:
        return value.lower() in ['true', 'yes', 'on', '1']
    return False

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': as_bool(os.environ.get('SQL_ECHO'))}
    IMAGE_PATH = os.environ.get("IMAGE_PATH") or 'D:\\RPGs\\Backdrops\\'
    THUMBNAIL_SUBFOLDER = os.environ.get("THUMBNAIL_SUBFOLDER") or 'thumbnails'

    TEMPLATES_AUTO_RELOAD = True
    DEBUG_MODE =  True