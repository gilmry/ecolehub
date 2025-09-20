"""
EcoleHub Stage 3 - Shop Service for Group Buying
Collaborative purchasing for EcoleHub families
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from .models_stage3 import ShopInterest, ShopOrder, ShopOrderItem, ShopProduct
from .mollie_service import mollie_service


class ShopCollaborativeService:
    """
    Service for collaborative buying system
    Parents express interest → Group orders when threshold met
    """

    def __init__(self, db: Session):
        self.db = db

    def get_products(
        self, category: Optional[str] = None, active_only: bool = True
    ) -> List[ShopProduct]:
        """Get available products for EcoleHub."""
        query = self.db.query(ShopProduct)

        if active_only:
            query = query.filter(ShopProduct.is_active)

        if category:
            query = query.filter(ShopProduct.category == category)

        return query.order_by(ShopProduct.created_at.desc()).all()

    def get_product_with_interest_count(self, product_id: UUID) -> Dict[str, Any]:
        """Get product with current interest count and users."""
        product = (
            self.db.query(ShopProduct).filter(ShopProduct.id == product_id).first()
        )
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        # Count total interest
        total_interest = (
            self.db.query(func.sum(ShopInterest.quantity))
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.status == "interested",
                )
            )
            .scalar()
            or 0
        )

        # Count interested users
        interested_users = (
            self.db.query(ShopInterest)
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.status == "interested",
                )
            )
            .all()
        )

        # Calculate group buying progress
        progress_percentage = (
            min((total_interest / product.min_quantity) * 100, 100)
            if product.min_quantity > 0
            else 100
        )
        can_order = total_interest >= product.min_quantity

        # Calculate Belgian price with tax
        tax_calculation = mollie_service.calculate_belgian_tax(
            float(product.base_price)
        )

        return {
            "product": product,
            "total_interest": total_interest,
            "interested_users_count": len(interested_users),
            "min_quantity": product.min_quantity,
            "progress_percentage": round(progress_percentage, 1),
            "can_order": can_order,
            "status": "ready" if can_order else "collecting_interest",
            "price_breakdown": tax_calculation,
            "interested_users": [
                {
                    "user_name": f"{interest.user.first_name} {interest.user.last_name}",
                    "quantity": interest.quantity,
                    "notes": interest.notes,
                }
                for interest in interested_users
            ],
        }

    def express_interest(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int = 1,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parent expresses interest in a product."""
        # Check if product exists
        product = (
            self.db.query(ShopProduct).filter(ShopProduct.id == product_id).first()
        )
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        # Check if user already expressed interest
        existing_interest = (
            self.db.query(ShopInterest)
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.user_id == user_id,
                )
            )
            .first()
        )

        if existing_interest:
            # Update existing interest
            existing_interest.quantity = quantity
            existing_interest.notes = notes
            existing_interest.status = "interested"
            self.db.commit()
            self.db.refresh(existing_interest)

            action = "updated"
            interest = existing_interest
        else:
            # Create new interest
            interest = ShopInterest(
                product_id=product_id,
                user_id=user_id,
                quantity=quantity,
                notes=notes,
                status="interested",
            )
            self.db.add(interest)
            self.db.commit()
            self.db.refresh(interest)

            action = "created"

        # Check if we've reached minimum quantity for group order
        total_interest = (
            self.db.query(func.sum(ShopInterest.quantity))
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.status == "interested",
                )
            )
            .scalar()
            or 0
        )

        threshold_reached = total_interest >= product.min_quantity

        result = {
            "success": True,
            "action": action,
            "interest_id": str(interest.id),
            "total_interest": total_interest,
            "min_quantity": product.min_quantity,
            "threshold_reached": threshold_reached,
            "message": f"Intérêt {'mis à jour' if action == 'updated' else 'enregistré'} pour {product.name}",
        }

        # If threshold reached, notify about potential group order
        if threshold_reached:
            result["message"] += f" - Seuil atteint ! Commande groupée possible."
            # TODO: Send notifications to interested parents
            # TODO: Create Celery task for order processing

        return result

    def cancel_interest(self, user_id: UUID, product_id: UUID) -> Dict[str, Any]:
        """Cancel interest in a product."""
        interest = (
            self.db.query(ShopInterest)
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.user_id == user_id,
                )
            )
            .first()
        )

        if not interest:
            raise HTTPException(status_code=404, detail="Intérêt non trouvé")

        self.db.delete(interest)
        self.db.commit()

        return {"success": True, "message": "Intérêt annulé"}

    def create_group_order(
        self, product_id: UUID, admin_user_id: UUID
    ) -> Dict[str, Any]:
        """
        Create group order when threshold is met
        Only for EcoleHub administrators or delegated parents
        """
        product = (
            self.db.query(ShopProduct).filter(ShopProduct.id == product_id).first()
        )
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        # Get all interested users
        interests = (
            self.db.query(ShopInterest)
            .filter(
                and_(
                    ShopInterest.product_id == product_id,
                    ShopInterest.status == "interested",
                )
            )
            .all()
        )

        if not interests:
            raise HTTPException(status_code=400, detail="Aucun intérêt pour ce produit")

        total_quantity = sum(interest.quantity for interest in interests)

        if total_quantity < product.min_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Quantité insuffisante ({total_quantity}/{product.min_quantity})",
            )

        # Calculate pricing with Belgian tax
        tax_calc = mollie_service.calculate_belgian_tax(float(product.base_price))
        unit_price_with_tax = Decimal(str(tax_calc["total_amount"]))
        total_order_price = unit_price_with_tax * total_quantity

        # Create group order
        order = ShopOrder(
            product_id=product_id,
            total_quantity=total_quantity,
            unit_price=unit_price_with_tax,
            total_price=total_order_price,
            status="pending",
        )

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        # Create individual order items for each interested parent
        for interest in interests:
            item_total = unit_price_with_tax * interest.quantity

            order_item = ShopOrderItem(
                order_id=order.id,
                user_id=interest.user_id,
                quantity=interest.quantity,
                unit_price=unit_price_with_tax,
                total_price=item_total,
                notes=interest.notes,
            )
            self.db.add(order_item)

            # Mark interest as confirmed
            interest.status = "confirmed"

        self.db.commit()

        # TODO: Create Celery task for Mollie payment processing
        # TODO: Send email notifications to parents

        return {
            "success": True,
            "order_id": str(order.id),
            "total_quantity": total_quantity,
            "total_price": float(total_order_price),
            "participants": len(interests),
            "message": f"Commande groupée créée pour {product.name}",
            "next_step": "payment_processing",
        }

    def get_user_orders(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user's order history."""
        order_items = (
            self.db.query(ShopOrderItem)
            .filter(ShopOrderItem.user_id == user_id)
            .order_by(ShopOrderItem.created_at.desc())
            .all()
        )

        result = []
        for item in order_items:
            result.append(
                {
                    "order_item_id": str(item.id),
                    "order_id": str(item.order_id),
                    "product_name": item.order.product.name,
                    "quantity": item.quantity,
                    "total_price": float(item.total_price),
                    "payment_status": item.payment_status,
                    "order_status": item.order.status,
                    "estimated_delivery": item.order.estimated_delivery.isoformat()
                    if item.order.estimated_delivery
                    else None,
                    "created_at": item.created_at.isoformat(),
                }
            )

        return result

    def get_product_categories(self) -> List[str]:
        """Get available product categories."""
        categories = self.db.query(ShopProduct.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]


# Global shop service function
def get_shop_service(db: Session) -> ShopCollaborativeService:
    return ShopCollaborativeService(db)
