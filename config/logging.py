LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(module)s - %(filename)s - %(message)s',
            'datefmt': '%d/%m/%Y %H:%M:%S %Z',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'general': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': 'logs/general.log',
            'formatter': 'simple',
        },
        'webhook': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': 'logs/webhook.log',
            'formatter': 'simple',
        },
        'job_applying': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': 'logs/job_applying.log',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'common': {
            'handlers': ['general'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'webhooks': {
            'handlers': ['webhook'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'job_applying': {
            'handlers': ['job_applying'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}