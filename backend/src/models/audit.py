#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define mixin for adding audit columns to tables
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String


class AuditMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=False)

