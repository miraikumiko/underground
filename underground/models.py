from sqlalchemy import Table, Column, Integer, String, Boolean, DECIMAL, Date, ForeignKey
from underground.database import metadata

User = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("username", String, nullable=False, unique=True, index=True),
    Column("password", String, nullable=False),
    Column("token", String, unique=True, index=True),
    Column("balance", DECIMAL(15, 12), nullable=False)
)

Payment = Table(
    "payments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("payment_id", Integer, nullable=False, unique=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
)

Promocode = Table(
    "promocodes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("code", String, nullable=False, unique=True, index=True),
    Column("days", Integer, nullable=False),
    Column("vds_id", Integer, ForeignKey("vds.id"), nullable=False)
)

IsoImage = Table(
    "iso_images",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, nullable=False, unique=True, index=True)
)

VDS = Table(
    "vds",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("cores", Integer, nullable=False),
    Column("ram", Integer, nullable=False),
    Column("disk_size", Integer, nullable=False),
    Column("ipv4", Boolean, nullable=False),
    Column("ipv6", Boolean, nullable=False),
    Column("price", Integer, nullable=False)
)

Node = Table(
    "nodes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("ip", String, nullable=False, unique=True, index=True),
    Column("cores", Integer, nullable=False),
    Column("cores_available", Integer, nullable=False),
    Column("ram", Integer, nullable=False),
    Column("ram_available", Integer, nullable=False),
    Column("disk_size", Integer, nullable=False),
    Column("disk_size_available", Integer, nullable=False)
)

Server = Table(
    "servers",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("vnc_port", Integer, nullable=False, index=True),
    Column("start_at", Date, nullable=False),
    Column("end_at", Date, nullable=False),
    Column("vds_id", Integer, ForeignKey("vds.id"), nullable=False),
    Column("node_id", Integer, ForeignKey("nodes.id"), nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
)
