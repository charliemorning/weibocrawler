# -*- coding: UTF-8 -*-

import logging


FORMAT = '%(asctime)-15s %(object)s %(message)s %(extra)s'

logging.basicConfig(format=FORMAT)

logger = logging.getLogger('weibo')
logger.setLevel(logging.INFO)


