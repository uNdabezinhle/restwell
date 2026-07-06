from asgiref.local import Local


_audit_context = Local()


def get_current_audit_user():
    return getattr(_audit_context, "user", None)


class AuditRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _audit_context.user = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _audit_context.user = None
