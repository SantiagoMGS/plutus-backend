from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
# 📚 basename="category": como no usamos queryset directo en la clase
# (sino get_queryset()), debemos darle un nombre base para las URLs.

urlpatterns = router.urls
