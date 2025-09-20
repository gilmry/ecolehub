"""
EcoleHub Stage 3 - Mollie Payment Service for Belgian Parents
Integration with Belgian payment methods (Bancontact, SEPA, PayPal)
"""

import logging
from typing import Any, Dict, Optional

from mollie.api.client import Client
from mollie.api.error import Error as MollieError


class MolliePaymentService:
    """
    Mollie payment service for EcoleHub
    Supports Belgian payment methods popular with parents
    """

    def __init__(self):
        # Import secrets manager
        from .secrets_manager import get_external_api_key

        api_key = get_external_api_key("mollie")
        if not api_key or api_key.startswith("test_mollie_key"):
            logging.warning(
                "⚠️ MOLLIE_API_KEY not configured or placeholder - using test mode"
            )
            api_key = "test_dHar4XY7LxsDOtmnkVtjNVWXLSlXsM"  # Test key

        self.client = Client()
        self.client.set_api_key(api_key)

        # Belgian context
        self.default_locale = "fr_BE"  # French Belgian
        self.default_currency = "EUR"

    def create_payment(
        self,
        amount: float,
        description: str,
        user_email: str,
        order_id: str,
        redirect_url: str,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment for EcoleHub parents

        Args:
            amount: Amount in EUR (e.g., 12.50)
            description: Payment description (e.g., "Commande T-shirt EcoleHub")
            user_email: Parent email for receipt
            order_id: Internal order reference
            redirect_url: Where to redirect after payment
            webhook_url: Webhook for payment status updates
        """
        try:
            # Belgian-optimized payment methods
            payment_methods = [
                "bancontact",  # Belgian bank card (most popular)
                "ideal",  # Dutch but used in Belgium
                "creditcard",  # Visa, Mastercard
                "paypal",  # Popular backup option
                "banktransfer",  # SEPA bank transfer
            ]

            payment_data = {
                "amount": {"currency": self.default_currency, "value": f"{amount:.2f}"},
                "description": f"EcoleHub - {description}",
                "redirectUrl": redirect_url,
                "metadata": {
                    "order_id": order_id,
                    "school": "EcoleHub",
                    "user_email": user_email,
                },
                "locale": self.default_locale,
                "method": payment_methods,  # Let user choose preferred method
            }

            if webhook_url:
                payment_data["webhookUrl"] = webhook_url

            payment = self.client.payments.create(payment_data)

            return {
                "success": True,
                "payment_id": payment.id,
                "payment_url": payment.checkout_url,
                "status": payment.status,
                "amount": float(payment.amount["value"]),
                "currency": payment.amount["currency"],
                "description": payment.description,
                "created_at": payment.created_at.isoformat(),
            }

        except MollieError as e:
            logging.error(f"❌ Mollie payment error: {e}")
            return {"success": False, "error": str(e), "error_type": "mollie_api_error"}
        except Exception as e:
            logging.error(f"❌ Payment service error: {e}")
            return {
                "success": False,
                "error": "Erreur système de paiement",
                "error_type": "system_error",
            }

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Mollie."""
        try:
            payment = self.client.payments.get(payment_id)

            return {
                "success": True,
                "payment_id": payment.id,
                "status": payment.status,
                "amount": float(payment.amount["value"]),
                "currency": payment.amount["currency"],
                "method": payment.method,
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
                "metadata": payment.metadata,
            }

        except MollieError as e:
            return {"success": False, "error": str(e)}

    def handle_webhook(self, payment_id: str) -> Dict[str, Any]:
        """
        Handle Mollie webhook for payment status updates
        Called automatically when payment status changes
        """
        try:
            payment = self.client.payments.get(payment_id)

            webhook_data = {
                "payment_id": payment.id,
                "status": payment.status,
                "amount": float(payment.amount["value"]),
                "metadata": payment.metadata,
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
            }

            # Log for EcoleHub records
            if payment.status == "paid":
                logging.info(
                    f"💰 Payment successful for EcoleHub: {payment_id} - {payment.amount['value']} EUR"
                )
            elif payment.status == "failed":
                logging.warning(f"❌ Payment failed: {payment_id}")

            return {"success": True, "webhook_data": webhook_data}

        except MollieError as e:
            logging.error(f"❌ Webhook error: {e}")
            return {"success": False, "error": str(e)}

    def get_supported_methods(self) -> list:
        """Get payment methods available in Belgium."""
        try:
            methods = self.client.methods.all()

            # Filter for Belgian-relevant methods
            belgian_methods = []
            for method in methods:
                if method.id in [
                    "bancontact",
                    "ideal",
                    "creditcard",
                    "paypal",
                    "banktransfer",
                ]:
                    belgian_methods.append(
                        {
                            "id": method.id,
                            "description": method.description,
                            "image": method.image,
                            "min_amount": float(method.minimum_amount["value"])
                            if method.minimum_amount
                            else 0,
                            "max_amount": float(method.maximum_amount["value"])
                            if method.maximum_amount
                            else 999999,
                        }
                    )

            return belgian_methods

        except MollieError:
            # Fallback methods for EcoleHub
            return [
                {
                    "id": "bancontact",
                    "description": "Bancontact",
                    "min_amount": 0.31,
                    "max_amount": 50000,
                },
                {
                    "id": "creditcard",
                    "description": "Carte de crédit",
                    "min_amount": 0.31,
                    "max_amount": 10000,
                },
                {
                    "id": "paypal",
                    "description": "PayPal",
                    "min_amount": 0.31,
                    "max_amount": 8000,
                },
            ]

    def calculate_belgian_tax(self, base_amount: float) -> Dict[str, float]:
        """
        Calculate Belgian tax (TVA 21%) for school purchases
        """
        tax_rate = 0.21  # Belgian VAT rate
        tax_amount = base_amount * tax_rate
        total_with_tax = base_amount + tax_amount

        return {
            "base_amount": round(base_amount, 2),
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(total_with_tax, 2),
            "currency": "EUR",
        }


# Global Mollie service instance
mollie_service = MolliePaymentService()
