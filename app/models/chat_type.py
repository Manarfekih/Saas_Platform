from enum import Enum


class ChatType(str, Enum):
    DOCUMENT = "document"
    GLOBAL = "global"