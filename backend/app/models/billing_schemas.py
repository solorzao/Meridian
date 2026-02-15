from app.models.base import CamelModel


class CheckoutRequest(CamelModel):
    success_url: str
    cancel_url: str


class PortalRequest(CamelModel):
    return_url: str
