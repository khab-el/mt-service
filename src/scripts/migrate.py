from yoyo import get_backend, read_migrations

from src.settings import settings

backend = get_backend(
    settings.DATABASE_URL
)
migrations = read_migrations("./migrations")


def apply_migration():
    with backend.lock():

        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))


# TODO create rol back only for last apply (need for k8s deploy api)
def rollback_migration():
    with backend.lock():
        # Rollback all migrations
        backend.rollback_migrations(backend.to_rollback(migrations))
