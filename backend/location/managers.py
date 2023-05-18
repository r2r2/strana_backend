from socket import inet_aton
from struct import unpack
from django.db.models import Manager


class LocationManager(Manager):
    """
    Менеджер локаций
    """

    def by_ip(self, ip):
        number = unpack('!L', inet_aton(ip))[0]
        queryset = super().get_queryset()
        return queryset.filter(start_ip__lte=number, end_ip__gte=number).order_by('end_ip', '-start_ip')
