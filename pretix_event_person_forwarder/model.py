import ssl
from dataclasses import dataclass
from enum import Enum

import httpx

# The constant includes all necessary error messages that can occurs, if you establish a connection to the Grafana API.
ERROR_MESSAGES: list = ["invalid API key", "Invalid API key", "Expired API key"]

class APIEndpoints(Enum):
    """The class includes all necessary API endpoint strings to connect the Pretix API"""

    api_prefix: str = "api"
    version_1: str = "v1"
    ORGANIZERS: str = f"/{api_prefix}/{version_1}/organizers"
    EVENTS: str = "events"
    ORDERS: str = "orders"
    QUESTIONS: str = "questions"

class RequestsMethods(Enum):
    """The class includes all necessary method values to establish an HTTP/ HTTPS connection to the Pretix API endpoints"""

    GET: str = "GET"
    PUT: str = "PUT"
    POST: str = "POST"
    PATCH: str = "PATCH"
    DELETE: str = "DELETE"

@dataclass
class APIModel:
    """The class includes all necessary variables to establish a connection to the Grafana API endpoints

    Args:
        host (str): Specify the host of the Grafana system
        token (str): Specify the access token of the Grafana system
        username (str): Specify the username of the Grafana system
        password (str): Specify the password of the Grafana system
        timeout (float): Specify the timeout of the Grafana system
        headers (dict): Specify the headers of the Grafana system
        http2_support (bool): Specify if you want to use HTTP/2
        ssl_context (ssl.SSLContext): Specify the custom ssl context of the Grafana system
        num_pools (int): Specify the number of the connection pool
        retries (any): Specify the number of the retries. Please use False as parameter to disable the retries
        follow_redirects (bool): Specify if redirections should be followed (default True)
    """

    host: str
    token: str = None
    username: str = None
    password: str = None
    headers: dict = None
    timeout: float = 10.0
    http2_support: bool = False
    ssl_context: ssl.SSLContext = httpx.create_ssl_context()
    num_pools: int = 10
    retries: any = 10
    follow_redirects: bool = True