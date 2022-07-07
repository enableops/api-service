from enum import Enum


class Auth(str, Enum):
    start = "/start"
    token = "/access_token"
    settings = "/settings"
    logout = "/logout"


class Sections(str, Enum):
    auth = "/auth"
