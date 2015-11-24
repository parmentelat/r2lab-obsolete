import logging

log_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'

# hard-wire for now
logging.basicConfig(
    level=logging.INFO,
#    level=logging.DEBUG,
    format = log_format,
    filename = 'imaging.log'
    )

logger = logging.getLogger('imaging')
