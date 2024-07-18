import secure
from fastapi import FastAPI


def add_security_headers(app: FastAPI) -> None:
    secure_server = secure.Server().set("Secure")
    hsts = secure.StrictTransportSecurity().include_subdomains().preload().max_age(31536000)
    referrer = secure.ReferrerPolicy().no_referrer()
    permissions_value = secure.PermissionsPolicy().geolocation("self").vibrate()
    cache_value = secure.CacheControl().must_revalidate()
    secure_headers = secure.Secure(
        server=secure_server,
        hsts=hsts,
        referrer=referrer,
        permissions=permissions_value,
        cache=cache_value,
    )

    @app.middleware("http")
    async def set_secure_headers(request, call_next):
        response = await call_next(request)
        secure_headers.framework.fastapi(response)
        return response
