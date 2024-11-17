from enum import Enum


class APIEndpoints(Enum):
    """The class includes all necessary API endpoint strings to connect the Pretix API"""

    api_prefix: str = "/api"
    version_1: str = "v1"