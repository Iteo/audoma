class BasicDatabaseRouter:
    route_app_labels = set()
    database_name = None

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.database_name
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.database_name
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == self.database_name
        return None


class AudomaApiRouter(BasicDatabaseRouter):
    route_app_labels = {"audoma_api"}
    database_name = "audoma_api"


class HealthCareApiRouter(BasicDatabaseRouter):
    route_app_labels = {"healthcare_api"}
    database_name = "healthcare_api"
