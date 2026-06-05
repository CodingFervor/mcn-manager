import time
import logging
import json

logger = logging.getLogger('api')


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/') and not request.path.startswith('/api/auth/'):
            start = time.perf_counter()
            response = self.get_response(request)
            elapsed_ms = (time.perf_counter() - start) * 1000
            response['X-Response-Time'] = f'{elapsed_ms:.1f}ms'
            if elapsed_ms > 500:
                logger.warning(f'SLOW {request.method} {request.path} {elapsed_ms:.1f}ms')
            elif elapsed_ms > 100:
                logger.info(f'SLOWISH {request.method} {request.path} {elapsed_ms:.1f}ms')
            return response
        return self.get_response(request)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/health/':
            from django.http import JsonResponse
            from django.db import connection
            from django.core.cache import cache

            checks = {}
            try:
                connection.ensure_connection()
                checks['db'] = 'ok'
            except Exception as e:
                checks['db'] = f'error: {e}'

            try:
                cache.set('_health', '1', 1)
                checks['cache'] = 'ok' if cache.get('_health') == '1' else 'error'
            except Exception:
                checks['cache'] = 'error'

            status = 200 if all(v == 'ok' for v in checks.values()) else 503
            return JsonResponse({
                'status': 'healthy' if status == 200 else 'degraded',
                'checks': checks,
                'version': '2.0.0',
            }, status=status)

        return self.get_response(request)
