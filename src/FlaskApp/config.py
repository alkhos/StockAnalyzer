import os

base_dir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    CACHE_TYPE = 'null'
    
    # set DB path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'app.db')

    # set tracking to false
    SQLALCHEMY_TRACK_MODIFICATIONS = False