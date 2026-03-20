"""
📚 SERIALIZER de Category.

Sencillo: muestra todos los campos y marca los de solo lectura.
El campo 'user' no se expone al frontend — se asigna automáticamente.
"""

from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):

    category_type_display = serializers.CharField(
        source="get_category_type_display",
        read_only=True,
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "category_type",
            "category_type_display",
            "icon",
            "color",
            "is_default",
        )
        read_only_fields = ("id", "is_default")

    def validate(self, attrs):
        """
        📚 Validación custom para evitar duplicados.
        Verifica que el usuario no tenga ya una categoría con el mismo nombre y tipo.
        """
        user = self.context["request"].user
        name = attrs.get("name", getattr(self.instance, "name", None))
        category_type = attrs.get(
            "category_type", getattr(self.instance, "category_type", None)
        )
        qs = Category.objects.filter(
            user=user, name=name, category_type=category_type
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"name": "Ya tienes una categoría con este nombre y tipo."}
            )
        return attrs
