import os

import ConfigParser

__all__ = ['config']

config = ConfigParser.SafeConfigParser()

env = 'PYTHON_ENV' in os.environ and os.environ['PYTHON_ENV'] or 'development'
if env == 'production':
    cfg = 'production.cfg'
elif env == 'development':
    cfg = 'development.cfg'
else:
    cfg = 'default.cfg'
config.read(os.path.join(os.path.dirname(__file__), cfg))
