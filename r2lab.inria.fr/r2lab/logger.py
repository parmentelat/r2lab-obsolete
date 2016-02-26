import logging
import logging.config

def init_logger(filename):

    logging_config = {
        'version' : 1,
        'disable_existing_loggers' : True,
        'formatters': { 
            'standard': { 
                'format': '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
                'datefmt': '%m-%d %H:%M:%S'
            },
            'shorter': { 
                'format': '%(asctime)s %(levelname)s %(message)s',
                'datefmt': '%d %H:%M:%S'
            },
        },
        'handlers': {
            'r2lab': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'standard',
                'filename' : filename,
            },
        },
        'loggers': {
            'r2lab': {
                'handlers': ['r2lab'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    return logging.getLogger('r2lab')
    


