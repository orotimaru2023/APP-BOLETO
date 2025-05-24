"""
Pacote principal da aplicação de boletos.
"""

__version__ = "1.0.0"

from . import db
from . import models
from . import schemas
from . import crud
from . import auth

__all__ = ['db', 'models', 'schemas', 'crud', 'auth']
