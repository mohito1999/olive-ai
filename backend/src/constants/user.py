from enum import Enum


class AuthProvider(str, Enum):
    SUPABASE = "SUPABASE"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DEFAULT = "DEFAULT"
