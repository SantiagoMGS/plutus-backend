from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.transactions"
    verbose_name = "Transacciones"

    def ready(self):
        """
        📚 ready() se ejecuta cuando Django carga la app.
        Aquí importamos los signals para que se registren.
        Sin este import, Django no sabría que existen los observers.
        """
        import apps.transactions.signals  # noqa: F401
