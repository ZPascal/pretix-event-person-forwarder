import os
from pretix_event_person_forwarder.model import APIModel
import httpx


def create_api_model_with_ssl(host: str, token: str, ca_bundle: str = None) -> APIModel:
    """Create APIModel with custom SSL context if CA bundle is provided"""
    if ca_bundle and os.path.exists(ca_bundle):
        ssl_context = httpx.create_ssl_context()
        ssl_context.load_verify_locations(ca_bundle)
    else:
        ssl_context = httpx.create_ssl_context()

    return APIModel(
        host=host,
        token=token,
        http2_support=False,
        timeout=30.0,
        ssl_context=ssl_context,
    )
