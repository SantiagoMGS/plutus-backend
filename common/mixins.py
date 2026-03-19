"""
📚 MIXINS — Comportamiento reutilizable para ViewSets.

📚 PATRÓN: Template Method (Refactoring Guru)
Un mixin define el "esqueleto" de una operación. Las clases que lo hereden
obtienen ese comportamiento automáticamente sin repetir código.

¿Por qué? Porque TODAS nuestras apps (accounts, transactions, loans, etc.)
necesitan filtrar los datos por usuario. Sin este mixin, tendríamos que
escribir get_queryset() con el mismo filtro en cada ViewSet. Con el mixin,
lo escribimos UNA VEZ y lo reutilizamos.
"""


class OwnerFilterMixin:
    """
    📚 Mixin que filtra automáticamente el queryset por el usuario autenticado.

    Uso: cualquier ViewSet que herede de este mixin solo mostrará
    los objetos del usuario logueado.

    Ejemplo:
        class AccountViewSet(OwnerFilterMixin, ModelViewSet):
            queryset = Account.objects.all()
            ...

        # GET /api/accounts/ → solo devuelve las cuentas de request.user
    """

    # 📚 owner_field es el nombre del campo FK al User en el modelo.
    # Por defecto es "user", pero puedes cambiarlo si tu modelo usa otro nombre.
    owner_field = "user"

    def get_queryset(self):
        """
        📚 get_queryset() es el método que DRF llama para obtener la lista
        de objetos. Aquí lo "interceptamos" para agregar un filtro.

        super().get_queryset() llama al get_queryset() original del ViewSet
        (que devuelve TODOS los objetos), y luego nosotros le aplicamos
        .filter(user=request.user) para que solo devuelva los del usuario actual.
        """
        queryset = super().get_queryset()
        return queryset.filter(**{self.owner_field: self.request.user})

    def perform_create(self, serializer):
        """
        📚 perform_create() se llama cuando se crea un nuevo objeto.
        Aquí asignamos automáticamente el campo "user" al usuario logueado.
        Así el frontend no necesita enviar user_id — se lo asignamos nosotros.
        """
        serializer.save(**{self.owner_field: self.request.user})
