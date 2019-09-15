import ipaddress

class IpMixin:
    def validate_ip(self, ip):
       ipaddress.ip_address(ip)

