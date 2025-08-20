import uuid
from typing import Callable
from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
RESPONSE_HEADER = "X-Request-ID"

def request_id_middleware(get_response: Callable[[HttpRequest], HttpResponse]):
    def middleware(request: HttpRequest) -> HttpResponse:
        rid = request.META.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.request_id = rid  # adjuntamos al request
        response = get_response(request)
        response[RESPONSE_HEADER] = rid  # devolvemos el id al cliente
        return response
    return middleware