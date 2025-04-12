from sqlalchemy import (
    MetaData,
    Table,
    Column,
    UUID,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    CheckConstraint,
    func,
    Integer,
    Index,
    text
)
from sqlalchemy.dialects.postgresql import ENUM
import enum

metadata = MetaData()

class UserRole(enum.Enum):
    EMPLOYEE = "employee"
    MODERATOR = "moderator"

userrole = ENUM('employee', 'moderator', name='userrole', create_type=False)

class City(enum.Enum):
    MOSCOW = "Москва"
    SPB = "Санкт-Петербург"
    KAZAN = "Казань"

city = ENUM('Москва', 'Санкт-Петербург', 'Казань', name='city', create_type=False)

class ReceptionStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    CLOSE = "close"

receptionstatus = ENUM('in_progress', 'close', name='receptionstatus', create_type=False)

class ProductType(enum.Enum):
    ELECTRONICS = "электроника"
    CLOTHES = "одежда"
    SHOES = "обувь"

producttype = ENUM('электроника', 'одежда', 'обувь', name='producttype', create_type=False)

users = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True, server_default=func.gen_random_uuid()),
    Column("email", String(255), unique=True, nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column("role", userrole, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Index("idx_users_email", "email"),
    Index("idx_users_role", "role"),
    CheckConstraint("role IN ('employee', 'moderator')", name="valid_user_roles")
)

pvz = Table(
    "pvz",
    metadata,
    Column("id", UUID, primary_key=True, server_default=func.gen_random_uuid()),
    Column("registration_date", DateTime, server_default=func.now()),
    Column("city", city, nullable=False),
    Column("moderator_id", UUID, ForeignKey("users.id"), nullable=False),
    Index("idx_pvz_city", "city"),
    Index("idx_pvz_moderator", "moderator_id"),
    CheckConstraint("city IN ('Москва', 'Санкт-Петербург', 'Казань')", name="valid_cities")
)

receptions = Table(
    "receptions",
    metadata,
    Column("id", UUID, primary_key=True, server_default=func.gen_random_uuid()),
    Column("date_time", DateTime, server_default=func.now()),
    Column("pvz_id", UUID, ForeignKey("pvz.id"), nullable=False),
    Column("status", receptionstatus, nullable=False, server_default="in_progress"),
    Index("idx_receptions_pvz_status", "pvz_id", "status"),
    Index("idx_receptions_datetime", "date_time"),
    CheckConstraint("status IN ('in_progress', 'close')", name="valid_reception_status")
)

products = Table(
    "products",
    metadata,
    Column("id", UUID, primary_key=True, server_default=func.gen_random_uuid()),
    Column("date_time", DateTime, server_default=func.now()),
    Column("type", producttype, nullable=False),
    Column("reception_id", UUID, ForeignKey("receptions.id"), nullable=False),
    Column("removed", Boolean, server_default="false"),
    Column("removal_order", Integer, autoincrement=True),
    Index("idx_products_reception", "reception_id"),
    Index("idx_products_removal_order", text("removal_order DESC")),
    Index("idx_products_type", "type"),
    CheckConstraint("type IN ('электроника', 'одежда', 'обувь')", name="valid_product_types")
)