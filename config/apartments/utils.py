from authentication.models import Domain

def get_domain_from_request(request):
    scheme = request.scheme                          # http or https
    host = request.get_host().split(":")[0]          # example.com
    full_domain = f"{scheme}://{host}"               # https://example.com

    return Domain.objects.filter(name=full_domain).first()
