#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define mixin for adding audit columns to tables
"""

from sqlalchemy import Column, DateTime, Text, text


class AuditMixin(object):
    created_at = Column(DateTime, server_default=text("current_timestamp_utc()"))
    created_by = Column(Text, nullable=False)
    updated_at = Column(DateTime, server_default=text("current_timestamp_utc()"))
    updated_by = Column(Text, nullable=False)

