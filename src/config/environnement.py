class Config(object):
    DEBUG = False
    TESTING = False
   
class ProductionConfig(Config):
    SECRET_KEY = b'{_M}?O0)$V+<@I-;0GK~TroHqACf9x'
    ENV = "production"

class DevelopmentConfig(Config):
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
    ENV = "development"
    DEBUG = True