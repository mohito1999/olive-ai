from enum import Enum


class CustomerSetType(str, Enum):
    FILE = "FILE"

class CustomerSetStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSED = "PROCESSED"

