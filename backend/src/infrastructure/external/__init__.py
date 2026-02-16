"""
Infrastructure - External Services

Integrações com serviços externos (Mercado Pago, Maps API, etc.).
"""

from .mercadopago_gateway import MercadoPagoGateway

__all__ = ["MercadoPagoGateway"]
