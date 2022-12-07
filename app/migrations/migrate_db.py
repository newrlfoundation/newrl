import os
import importlib

from app.config.Configuration import Configuration
from app.config.constants import DB_MIGRATIONS_PATH, NEWRL_DB

db_path = NEWRL_DB


def run_migrations():
    migrations = os.listdir(DB_MIGRATIONS_PATH)
    migrations = filter(lambda migration: '.py' in migration, migrations)
    for migration in migrations:
        print(migration)
        migration = migration.replace('.py', '')
        path = DB_MIGRATIONS_PATH.replace('/', '.')
        migration = importlib.import_module(path + '.' + migration)
        migration.migrate()


if __name__ == '__main__':
    db_path = '../' + db_path
    Configuration.init_values()
    Configuration.init_values_in_db()
    run_migrations()
