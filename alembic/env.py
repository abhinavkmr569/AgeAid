import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, create_engine # <--- Added create_engine

from alembic import context

# ---------------------------------------------------------
# 1. ADD PARENT DIRECTORY TO PATH
# This allows us to import 'database.py' and 'models.py'
# even though this script runs inside the 'alembic/' folder.
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------
# 2. IMPORT YOUR PROJECT DATA
# ---------------------------------------------------------
from models import Base       # To see your table structure
from database import DATABASE_URL # To get the correct Connection String

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# 3. SET METADATA
# This tells Alembic where your tables are defined
# ---------------------------------------------------------
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL.
    """
    # Use the URL imported from database.py instead of alembic.ini
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    
    # ---------------------------------------------------------
    # 4. CREATE ENGINE MANUALLY
    # We ignore the alembic.ini url and use our robust DATABASE_URL
    # ---------------------------------------------------------
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()