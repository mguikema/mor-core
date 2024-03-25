from django.conf import settings


class DatabaseRouter:
    def db_for_read(self, model, **hints):
        # Reads go to the standby node or pool
        return settings.READONLY_DATABASE_KEY

    def db_for_write(self, model, **hints):
        # Writes always go to the primary node.
        return settings.DEFAULT_DATABASE_KEY

    def allow_relation(self, obj1, obj2, **hints):
        # We have a fully replicated cluster, so we can allow
        # relationships between objects from different databases
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Only allow migrations on the primary
        return db == settings.DEFAULT_DATABASE_KEY
