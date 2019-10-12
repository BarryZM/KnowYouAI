import logging
import time
import config

logging.basicConfig(level=logging.DEBUG,
                    stream=open(config.LOGGING.format(int(time.time())), "w", encoding="utf-8"),
                    format='[%(asctime)s-%(filename)s] [%(levelname)s] %(message)s',
                    datefmt='%Y %H:%M:%S',
                    )
global_logger = logging.getLogger(__name__)
