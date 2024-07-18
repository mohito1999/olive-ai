# -*- coding: utf-8 -*-
from .base import ApplicationException


class DatabaseException(ApplicationException):
    """Generic Database Exception"""


class RecordIntegrityException(DatabaseException):
    """Record causes integrity constraint voilation"""


class RecordValidationException(DatabaseException):
    """Record fails schema validation"""


class RecordNotFoundException(DatabaseException):
    """Record not found in database"""
