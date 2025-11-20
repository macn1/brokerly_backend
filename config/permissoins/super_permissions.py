import logging
from rest_framework.permissions import BasePermission
from authentication.models import Domain, User

logger = logging.getLogger(__name__)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsDomainAdmin(BasePermission):
    def has_permission(self, request, view):
        logger.info("---- Entered IsDomainAdmin Permission ----")

        user: User = request.user
        origin = request.META.get("HTTP_ORIGIN")

        logger.info(f"Origin: {origin}")
        logger.info(f"User: {user.email if user.is_authenticated else None}")

        if not origin:
            logger.warning("Blocked: No origin header found")
            return False

        try:
            # 🔥 Change applied here
            domain = Domain.objects.get(name=origin)
            logger.info(f"Matched Domain -> {domain.name}")
        except Domain.DoesNotExist:
            logger.warning("Blocked: No domain matched for origin")
            return False

        request.domain = domain

        access = user.domain_id == domain.id
        logger.info(f"Access Granted: {access}")

        return access
