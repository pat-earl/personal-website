# config.py

class Config(object):
    TEMPLATES_AUTO_RELOAD = True
    HOST='0.0.0.0'
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    HOST='127.0.0.1'