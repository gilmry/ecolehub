"""
EcoleHub Stage 3 Models - Extends Stage 2 with Shop and Education
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, CheckConstraint, DECIMAL, Date
from .db_types import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# Import previous stage models
from .models_stage2 import Base, User, Child, Conversation, Message, Event
from .models_stage1 import SELService, SELTransaction, SELBalance, SELCategory

class ShopProduct(Base):
    __tablename__ = "shop_products"
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))  # MinIO file path
    printful_id = Column(String(100))  # For custom EcoleHub items
    category = Column(String(50), nullable=False)
    min_quantity = Column(Integer, default=10)  # Minimum for group order
    is_active = Column(Boolean, default=True)
    created_by = Column(UUIDType(), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    interests = relationship("ShopInterest", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("ShopOrder", back_populates="product")

class ShopInterest(Base):
    __tablename__ = "shop_interests"
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUIDType(), ForeignKey("shop_products.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)
    notes = Column(Text)  # Size, color, special requirements
    status = Column(String(20), default='interested')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('interested', 'confirmed', 'cancelled')",
            name="valid_interest_status"
        ),
        CheckConstraint("quantity > 0", name="positive_quantity"),
    )
    
    # Relationships
    product = relationship("ShopProduct", back_populates="interests")
    user = relationship("User")

class ShopOrder(Base):
    __tablename__ = "shop_orders"
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUIDType(), ForeignKey("shop_products.id"), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    mollie_payment_id = Column(String(100))  # Mollie payment reference
    printful_order_id = Column(String(100))  # Printful order reference
    status = Column(String(30), default='pending')
    estimated_delivery = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'payment_pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')",
            name="valid_order_status"
        ),
        CheckConstraint("total_quantity > 0", name="positive_total_quantity"),
        CheckConstraint("unit_price > 0", name="positive_unit_price"),
        CheckConstraint("total_price > 0", name="positive_total_price"),
    )
    
    # Relationships
    product = relationship("ShopProduct", back_populates="orders")
    order_items = relationship("ShopOrderItem", back_populates="order", cascade="all, delete-orphan")

class ShopOrderItem(Base):
    __tablename__ = "shop_order_items"
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUIDType(), ForeignKey("shop_orders.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    notes = Column(Text)
    payment_status = Column(String(20), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'refunded')",
            name="valid_payment_status"
        ),
        CheckConstraint("quantity > 0", name="positive_item_quantity"),
    )
    
    # Relationships
    order = relationship("ShopOrder", back_populates="order_items")
    user = relationship("User")

class EducationResource(Base):
    __tablename__ = "education_resources"
    
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 'homework', 'calendar', 'forms', 'announcements'
    class_name = Column(String(10))  # For class-specific resources
    file_url = Column(String(500))  # MinIO file path
    file_type = Column(String(50))  # pdf, doc, image, etc.
    file_size = Column(Integer)  # in bytes
    is_public = Column(Boolean, default=False)  # Public or parent-only
    created_by = Column(UUIDType(), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('homework', 'calendar', 'forms', 'announcements', 'resources')",
            name="valid_education_category"
        ),
        CheckConstraint(
            "class_name IS NULL OR class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')",
            name="valid_education_class"
        ),
    )
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    access_grants = relationship("ResourceAccess", back_populates="resource", cascade="all, delete-orphan")

class ResourceAccess(Base):
    __tablename__ = "resource_access"
    
    resource_id = Column(UUIDType(), ForeignKey("education_resources.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    access_type = Column(String(20), default='read')
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "access_type IN ('read', 'write', 'admin')",
            name="valid_access_type"
        ),
    )
    
    # Relationships
    resource = relationship("EducationResource", back_populates="access_grants")
    user = relationship("User")

# Extend User model with Stage 3 relationships
User.shop_products_created = relationship("ShopProduct", foreign_keys="ShopProduct.created_by", back_populates="creator")
User.shop_interests = relationship("ShopInterest", back_populates="user")
User.shop_order_items = relationship("ShopOrderItem", back_populates="user")
User.education_resources_created = relationship("EducationResource", foreign_keys="EducationResource.created_by", back_populates="creator")
User.resource_access_grants = relationship("ResourceAccess", back_populates="user")
