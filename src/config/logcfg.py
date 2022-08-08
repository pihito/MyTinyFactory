logger_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s :: %(levelname)s :: %(threadName)s :: %(module)s :: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': "fichier_de_log.log",
            'formatter': 'default',
            'encoding': 'utf8',
        },
    },
    'root': {
        'level': "DEBUG",
        'handlers': ['console', 'file']
    }
}