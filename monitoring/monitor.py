from django.db import models
import logging
import threading
import psutil
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings

class MonitoringMetrics(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    active_threads = models.IntegerField()
    memory_usage = models.FloatField()
    cpu_usage = models.FloatField()
    message_count = models.IntegerField()
    error_count = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
        ]

class SystemMonitor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        self.process = psutil.Process()
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Monitoring thread ni boshlash"""
        thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="system_monitor"
        )
        thread.start()
    
    def _monitoring_loop(self):
        while True:
            try:
                metrics = self._collect_metrics()
                self._save_metrics(metrics)
                self._check_alerts(metrics)
                time.sleep(settings.MONITORING_INTERVAL)
            except Exception as e:
                logging.error(f"Monitoring error: {str(e)}")
    
    def _collect_metrics(self):
        """Tizim metrikalarini yig'ish"""
        return {
            'active_threads': len(threading.enumerate()),
            'memory_usage': self.process.memory_percent(),
            'cpu_usage': self.process.cpu_percent(),
            'message_count': self._get_message_count(),
            'error_count': self._get_error_count()
        }
    
    def _save_metrics(self, metrics):
        """Metrikalarni saqlash"""
        MonitoringMetrics.objects.create(**metrics)
        
        # Eski metrikalarni o'chirish (7 kundan eski)
        old_date = datetime.now() - timedelta(days=7)
        MonitoringMetrics.objects.filter(timestamp__lt=old_date).delete()
    
    def _check_alerts(self, metrics):
        """Alert tekshirish"""
        if metrics['memory_usage'] > settings.MEMORY_ALERT_THRESHOLD:
            self._send_alert('memory', metrics['memory_usage'])
            
        if metrics['error_count'] > settings.ERROR_ALERT_THRESHOLD:
            self._send_alert('errors', metrics['error_count'])
    
    def _send_alert(self, alert_type, value):
        """Alert yuborish"""
        # Alert yuborilganidan keyin 1 soat davomida qayta yuborilmasligi uchun
        cache_key = f"alert_{alert_type}"
        if not cache.get(cache_key):
            logging.critical(f"ALERT: {alert_type} threshold exceeded: {value}")
            # TODO: Email/Telegram orqali xabar yuborish
            cache.set(cache_key, True, timeout=3600)  # 1 soat 