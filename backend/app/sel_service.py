from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from .models_stage1 import SELBalance, SELCategory, SELService, SELTransaction, User
from .schemas_stage1 import SELServiceCreate, SELTransactionCreate


class SELBusinessLogic:
    """
    Business logic for the SEL (Système d'Échange Local) system.
    Handles Belgian-specific rules and constraints.
    """

    def __init__(self, db: Session):
        self.db = db

    # Balance Management
    def get_or_create_balance(self, user_id: UUID) -> SELBalance:
        """Get user balance or create with initial 120 units."""
        balance = (
            self.db.query(SELBalance).filter(SELBalance.user_id == user_id).first()
        )
        if not balance:
            balance = SELBalance(user_id=user_id, balance=120)
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        return balance

    def validate_transaction_balance(
        self, from_user_id: UUID, to_user_id: UUID, units: int
    ) -> dict:
        """
        Validate if transaction is possible within Belgian SEL limits.
        Returns: {valid: bool, message: str, balances: dict}
        """
        from_balance = self.get_or_create_balance(from_user_id)
        to_balance = self.get_or_create_balance(to_user_id)

        # Calculate new balances
        new_from_balance = from_balance.balance - units
        new_to_balance = to_balance.balance + units

        # Check Belgian limits: -300 to +600
        if new_from_balance < -300:
            return {
                "valid": False,
                "message": f"Transaction refusée: votre solde deviendrait {new_from_balance} unités (limite: -300)",
                "balances": {"from": from_balance.balance, "to": to_balance.balance},
            }

        if new_to_balance > 600:
            return {
                "valid": False,
                "message": f"Transaction refusée: le destinataire dépasserait {new_to_balance} unités (limite: +600)",
                "balances": {"from": from_balance.balance, "to": to_balance.balance},
            }

        return {
            "valid": True,
            "message": "Transaction autorisée",
            "balances": {
                "from": {"current": from_balance.balance, "after": new_from_balance},
                "to": {"current": to_balance.balance, "after": new_to_balance},
            },
        }

    # Service Management
    def create_service(
        self, user_id: UUID, service_data: SELServiceCreate
    ) -> SELService:
        """Create a new SEL service with optional category proposal."""

        # Si c'est une proposition de nouvelle catégorie
        if service_data.category == "proposition" and service_data.new_category_name:
            # Créer le service avec le nom de la nouvelle catégorie dans la description
            enhanced_description = f"[PROPOSITION: {service_data.new_category_name}] {service_data.description or ''}"

            final_category = "proposition"

            service = SELService(
                user_id=user_id,
                title=service_data.title,
                description=enhanced_description,
                category=final_category,
                units_per_hour=service_data.units_per_hour,
            )
        else:
            # Validate category exists for regular services
            category = (
                self.db.query(SELCategory)
                .filter(SELCategory.name == service_data.category)
                .first()
            )
            if not category:
                # Auto-create missing category for smoother UX/tests
                category = SELCategory(name=service_data.category)
                self.db.add(category)
                self.db.commit()

            service = SELService(
                user_id=user_id,
                title=service_data.title,
                description=service_data.description,
                category=service_data.category,
                units_per_hour=service_data.units_per_hour,
            )

        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def get_available_services(
        self, requesting_user_id: UUID, category: Optional[str] = None, limit: int = 50
    ) -> List[SELService]:
        """Get available services (excluding own services) with user information."""
        from sqlalchemy.orm import joinedload

        query = (
            self.db.query(SELService)
            .options(joinedload(SELService.user))
            .filter(
                and_(
                    SELService.is_active,
                    SELService.user_id != requesting_user_id,
                )
            )
        )

        if category:
            query = query.filter(SELService.category == category)

        return query.order_by(desc(SELService.created_at)).limit(limit).all()

    # Transaction Management
    def create_transaction(
        self, from_user_id: UUID, transaction_data: SELTransactionCreate
    ) -> SELTransaction:
        """
        Create a new SEL transaction with validation.
        """
        # Validate users exist and are different
        if from_user_id == transaction_data.to_user_id:
            raise HTTPException(
                status_code=400,
                detail="Impossible de créer une transaction avec soi-même",
            )

        from_user = self.db.query(User).filter(User.id == from_user_id).first()
        to_user = (
            self.db.query(User).filter(User.id == transaction_data.to_user_id).first()
        )

        if not from_user or not to_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Validate service exists and is active
        service = None
        if transaction_data.service_id:
            service = (
                self.db.query(SELService)
                .filter(
                    and_(
                        SELService.id == transaction_data.service_id,
                        SELService.is_active,
                    )
                )
                .first()
            )
            if not service:
                raise HTTPException(
                    status_code=404, detail="Service non trouvé ou inactif"
                )

        # Validate balance limits
        validation = self.validate_transaction_balance(
            from_user_id, transaction_data.to_user_id, transaction_data.units
        )

        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["message"])

        # Create transaction
        transaction = SELTransaction(
            from_user_id=from_user_id,
            to_user_id=transaction_data.to_user_id,
            service_id=transaction_data.service_id,
            units=transaction_data.units,
            description=transaction_data.description,
            status="pending",
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def approve_transaction(
        self, transaction_id: UUID, approving_user_id: UUID
    ) -> SELTransaction:
        """
        Approve a transaction and update balances.
        Only the recipient (to_user) can approve.
        """
        transaction = (
            self.db.query(SELTransaction)
            .filter(SELTransaction.id == transaction_id)
            .first()
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        # Only recipient can approve
        if transaction.to_user_id != approving_user_id:
            raise HTTPException(
                status_code=403,
                detail="Seul le destinataire peut approuver cette transaction",
            )

        if transaction.status != "pending":
            raise HTTPException(
                status_code=400, detail=f"Transaction déjà {transaction.status}"
            )

        # Re-validate balance limits (in case balances changed)
        validation = self.validate_transaction_balance(
            transaction.from_user_id, transaction.to_user_id, transaction.units
        )

        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Transaction impossible: {validation['message']}",
            )

        # Update balances
        from_balance = self.get_or_create_balance(transaction.from_user_id)
        to_balance = self.get_or_create_balance(transaction.to_user_id)

        from_balance.balance -= transaction.units
        from_balance.total_given += transaction.units

        to_balance.balance += transaction.units
        to_balance.total_received += transaction.units

        # Update transaction
        transaction.status = "approved"
        transaction.completed_at = func.now()

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def cancel_transaction(
        self, transaction_id: UUID, cancelling_user_id: UUID
    ) -> SELTransaction:
        """
        Cancel a pending transaction.
        Only sender or recipient can cancel.
        """
        transaction = (
            self.db.query(SELTransaction)
            .filter(SELTransaction.id == transaction_id)
            .first()
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        # Only sender or recipient can cancel
        if (
            transaction.from_user_id != cancelling_user_id
            and transaction.to_user_id != cancelling_user_id
        ):
            raise HTTPException(
                status_code=403, detail="Vous ne pouvez pas annuler cette transaction"
            )

        if transaction.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Impossible d'annuler une transaction {transaction.status}",
            )

        transaction.status = "cancelled"
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    # Dashboard and Statistics
    def get_user_dashboard(self, user_id: UUID) -> dict:
        """Get SEL dashboard data for a user."""
        balance = self.get_or_create_balance(user_id)

        # Count active services
        active_services = (
            self.db.query(func.count(SELService.id))
            .filter(and_(SELService.user_id == user_id, SELService.is_active))
            .scalar()
        )

        # Count pending transactions
        pending_transactions = (
            self.db.query(func.count(SELTransaction.id))
            .filter(
                and_(
                    or_(
                        SELTransaction.from_user_id == user_id,
                        SELTransaction.to_user_id == user_id,
                    ),
                    SELTransaction.status == "pending",
                )
            )
            .scalar()
        )

        # Recent transactions
        recent_transactions = (
            self.db.query(SELTransaction)
            .filter(
                or_(
                    SELTransaction.from_user_id == user_id,
                    SELTransaction.to_user_id == user_id,
                )
            )
            .order_by(desc(SELTransaction.created_at))
            .limit(10)
            .all()
        )

        # Available services from others
        available_services = self.get_available_services(user_id, limit=20)

        return {
            "balance": balance,
            "active_services": active_services,
            "pending_transactions": pending_transactions,
            "recent_transactions": recent_transactions,
            "available_services": available_services,
        }

    def get_categories(self) -> List[SELCategory]:
        """Get all SEL categories."""
        return self.db.query(SELCategory).order_by(SELCategory.name).all()
