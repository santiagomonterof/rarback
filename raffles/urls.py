from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from raffles.api import UserViewSet, RaffleViewSet, ParticipatingUserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'raffles', RaffleViewSet)
router.register(r'participating_users', ParticipatingUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-token-auth/', views.obtain_auth_token)
]
