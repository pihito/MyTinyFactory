# -*- encoding: utf-8 -*-
import datetime

class Config(object):
    # -----------------------------------------------------
    # Application configurations
    # ------------------------------------------------------
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'ieodnsd45kjzsl89'
    PORT = 8080
    HOST = 'localhost'

    # -----------------------------------------------------
    # ESI Configs
    # -----------------------------------------------------
    ESI_DATASOURCE = 'tranquility'  # Change it to 'singularity' to use the test server
    ESI_SWAGGER_JSON = 'https://esi.tech.ccp.is/latest/swagger.json?datasource=%s' % ESI_DATASOURCE
    ESI_SECRET_KEY = ' O3MQGGULEgVdfUAIycdJvGJ0b0MZu9AwlvVKUM8x'  # your secret key
    ESI_CLIENT_ID = 'd792e8ee580b400c8dd9eebd3c468cce'  # your client ID
    ESI_CALLBACK = 'http://%s:%d/sso/callback' % (HOST, PORT)  # the callback URI you gave CCP
    ESI_USER_AGENT = 'MYINDUSTRIALBUISINESS_DEV'

    # ------------------------------------------------------
    # Session settings for flask login
    # ------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    ENV = 'developement'


class ProductionConfig(Config):
    pass

myConfig = DevelopmentConfig()