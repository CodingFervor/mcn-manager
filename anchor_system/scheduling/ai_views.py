from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta, date
import hashlib
import json

from .ai_engine import (
    GMVPredictor, SmartScheduler, AnchorProfiler,
    AnomalyDetector, InsightEngine, AnchorMatcher
)


def _cache_key(prefix, **kwargs):
    raw = json.dumps(kwargs, sort_keys=True, default=str)
    return f'ai:{prefix}:{hashlib.md5(raw.encode()).hexdigest()}'


class AIViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def predict(self, request):
        params = {
            'days': min(max(int(request.query_params.get('days', 7)), 1), 30),
            'store_id': request.query_params.get('store_id', ''),
            'employee_id': request.query_params.get('employee_id', ''),
        }
        key = _cache_key('predict', **params)
        data = cache.get(key)
        if data is None:
            data = GMVPredictor.predict(days=params['days'], store_id=params['store_id'] or None, employee_id=params['employee_id'] or None)
            cache.set(key, data, 120)
        return Response(data)

    @action(detail=False, methods=['get'])
    def schedule(self, request):
        target = request.query_params.get('date')
        target_date = None
        if target:
            try:
                target_date = date.fromisoformat(target)
            except ValueError:
                pass
        store_id = request.query_params.get('store_id', '')
        key = _cache_key('schedule', date=target_date, store_id=store_id)
        data = cache.get(key)
        if data is None:
            data = SmartScheduler.recommend(target_date=target_date, store_id=store_id or None)
            cache.set(key, data, 120)
        return Response(data)

    @action(detail=False, methods=['get'])
    def anchor(self, request):
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({'status': 'error', 'message': '请提供 employee_id'}, status=400)
        key = _cache_key('anchor', employee_id=employee_id)
        data = cache.get(key)
        if data is None:
            data = AnchorProfiler.analyze(int(employee_id))
            cache.set(key, data, 180)
        return Response(data)

    @action(detail=False, methods=['get'])
    def anomaly(self, request):
        days = min(max(int(request.query_params.get('days', 7)), 1), 30)
        key = _cache_key('anomaly', days=days)
        data = cache.get(key)
        if data is None:
            data = AnomalyDetector.detect(days=days)
            cache.set(key, data, 120)
        return Response(data)

    @action(detail=False, methods=['get'])
    def insights(self, request):
        key = _cache_key('insights')
        data = cache.get(key)
        if data is None:
            data = InsightEngine.generate()
            cache.set(key, data, 120)
        return Response(data)

    @action(detail=False, methods=['get'])
    def match(self, request):
        store_id = request.query_params.get('store_id', '')
        key = _cache_key('match', store_id=store_id)
        data = cache.get(key)
        if data is None:
            data = AnchorMatcher.match(store_id=store_id or None)
            cache.set(key, data, 180)
        return Response(data)
