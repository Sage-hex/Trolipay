"""initial schema

Revision ID: 20260216_0001
Revises: None
Create Date: 2026-02-16 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260216_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("store_code", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_code"),
    )
    op.create_index(op.f("ix_business_name"), "business", ["name"], unique=False)
    op.create_index(op.f("ix_business_store_code"), "business", ["store_code"], unique=True)

    op.create_table(
        "customer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("channel_type", sa.String(), nullable=False),
        sa.Column("channel_user_id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "channel_type", "channel_user_id", name="uq_customer_business_channel_user"),
    )
    op.create_index(op.f("ix_customer_business_id"), "customer", ["business_id"], unique=False)
    op.create_index(op.f("ix_customer_channel_type"), "customer", ["channel_type"], unique=False)
    op.create_index(op.f("ix_customer_channel_user_id"), "customer", ["channel_user_id"], unique=False)

    op.create_table(
        "delivery_zone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("fee_kobo", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_delivery_zone_business_id"), "delivery_zone", ["business_id"], unique=False)

    op.create_table(
        "payout_profile",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("bank_name", sa.String(), nullable=False),
        sa.Column("account_number", sa.String(), nullable=False),
        sa.Column("account_name", sa.String(), nullable=False),
        sa.Column("paystack_subaccount_code", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.PrimaryKeyConstraint("business_id"),
        sa.UniqueConstraint("business_id"),
    )

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("base_price_kobo", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_business_id"), "product", ["business_id"], unique=False)
    op.create_index(op.f("ix_product_name"), "product", ["name"], unique=False)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_user_business_id"), "user", ["business_id"], unique=False)
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("channel_type", sa.String(), nullable=False),
        sa.Column("channel_thread_id", sa.String(), nullable=False),
        sa.Column("current_state", sa.String(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_business_id"), "conversation", ["business_id"], unique=False)
    op.create_index(op.f("ix_conversation_channel_thread_id"), "conversation", ["channel_thread_id"], unique=False)
    op.create_index(op.f("ix_conversation_channel_type"), "conversation", ["channel_type"], unique=False)
    op.create_index(op.f("ix_conversation_customer_id"), "conversation", ["customer_id"], unique=False)

    op.create_table(
        "message_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("channel_type", sa.String(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_log_business_id"), "message_log", ["business_id"], unique=False)

    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("channel_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("subtotal_kobo", sa.Integer(), nullable=False),
        sa.Column("delivery_fee_kobo", sa.Integer(), nullable=False),
        sa.Column("total_kobo", sa.Integer(), nullable=False),
        sa.Column("platform_fee_kobo", sa.Integer(), nullable=False),
        sa.Column("business_payout_kobo", sa.Integer(), nullable=False),
        sa.Column("delivery_zone_id", sa.Integer(), nullable=True),
        sa.Column("delivery_address", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.id"]),
        sa.ForeignKeyConstraint(["delivery_zone_id"], ["delivery_zone.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_business_id"), "order", ["business_id"], unique=False)
    op.create_index(op.f("ix_order_channel_type"), "order", ["channel_type"], unique=False)
    op.create_index(op.f("ix_order_customer_id"), "order", ["customer_id"], unique=False)
    op.create_index(op.f("ix_order_status"), "order", ["status"], unique=False)

    op.create_table(
        "order_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("name_snapshot", sa.String(), nullable=False),
        sa.Column("unit_price_kobo", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total_kobo", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["order.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_item_order_id"), "order_item", ["order_id"], unique=False)

    op.create_table(
        "payment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("amount_kobo", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("paystack_reference", sa.String(), nullable=True),
        sa.Column("authorization_url", sa.String(), nullable=True),
        sa.Column("raw_event_json", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["order.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("paystack_reference"),
    )
    op.create_index(op.f("ix_payment_order_id"), "payment", ["order_id"], unique=False)
    op.create_index(op.f("ix_payment_paystack_reference"), "payment", ["paystack_reference"], unique=True)
    op.create_index(op.f("ix_payment_status"), "payment", ["status"], unique=False)

    op.create_table(
        "receipt",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("receipt_number", sa.String(), nullable=False),
        sa.Column("pdf_url", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["order.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_receipt_order_id"), "receipt", ["order_id"], unique=False)
    op.create_index(op.f("ix_receipt_receipt_number"), "receipt", ["receipt_number"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_receipt_receipt_number"), table_name="receipt")
    op.drop_index(op.f("ix_receipt_order_id"), table_name="receipt")
    op.drop_table("receipt")

    op.drop_index(op.f("ix_payment_status"), table_name="payment")
    op.drop_index(op.f("ix_payment_paystack_reference"), table_name="payment")
    op.drop_index(op.f("ix_payment_order_id"), table_name="payment")
    op.drop_table("payment")

    op.drop_index(op.f("ix_order_item_order_id"), table_name="order_item")
    op.drop_table("order_item")

    op.drop_index(op.f("ix_order_status"), table_name="order")
    op.drop_index(op.f("ix_order_customer_id"), table_name="order")
    op.drop_index(op.f("ix_order_channel_type"), table_name="order")
    op.drop_index(op.f("ix_order_business_id"), table_name="order")
    op.drop_table("order")

    op.drop_index(op.f("ix_message_log_business_id"), table_name="message_log")
    op.drop_table("message_log")

    op.drop_index(op.f("ix_conversation_customer_id"), table_name="conversation")
    op.drop_index(op.f("ix_conversation_channel_type"), table_name="conversation")
    op.drop_index(op.f("ix_conversation_channel_thread_id"), table_name="conversation")
    op.drop_index(op.f("ix_conversation_business_id"), table_name="conversation")
    op.drop_table("conversation")

    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_index(op.f("ix_user_business_id"), table_name="user")
    op.drop_table("user")

    op.drop_index(op.f("ix_product_name"), table_name="product")
    op.drop_index(op.f("ix_product_business_id"), table_name="product")
    op.drop_table("product")

    op.drop_table("payout_profile")

    op.drop_index(op.f("ix_delivery_zone_business_id"), table_name="delivery_zone")
    op.drop_table("delivery_zone")

    op.drop_index(op.f("ix_customer_channel_user_id"), table_name="customer")
    op.drop_index(op.f("ix_customer_channel_type"), table_name="customer")
    op.drop_index(op.f("ix_customer_business_id"), table_name="customer")
    op.drop_table("customer")

    op.drop_index(op.f("ix_business_store_code"), table_name="business")
    op.drop_index(op.f("ix_business_name"), table_name="business")
    op.drop_table("business")
