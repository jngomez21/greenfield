import os

from alembic import context
from sqlalchemy import create_engine

import greenfield.tasks.models  # noqa: F401  (registra los modelos en Base.metadata)
from greenfield.config import sqlalchemy_url
from greenfield.db import Base

# Render entrega `postgresql://…`: se normaliza igual que en la app (T14).
url = context.config.get_main_option("sqlalchemy.url") or sqlalchemy_url(os.environ["DATABASE_URL"])

with create_engine(url).connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
