from concurrent.futures import ThreadPoolExecutor
import threading
import psutil
import logging
from django.conf import settings
from functools import wraps

class ThreadManager:
    _instance = None
    _lock = threading.Lock()
    _executor = ThreadPoolExecutor(
        max_workers=settings.MAX_WORKER_THREADS,
        thread_name_prefix="announcement_"
    )
    _active_tasks = {}  # {announcement_id: future}
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def start_task(self, announcement_id, task_func):
        """Thread ni xavfsiz ravishda boshlash"""
        if announcement_id in self._active_tasks:
            self.stop_task(announcement_id)
            
        future = self._executor.submit(self._task_wrapper, announcement_id, task_func)
        self._active_tasks[announcement_id] = future
        return future
    
    def stop_task(self, announcement_id):
        """Thread ni xavfsiz ravishda to'xtatish"""
        if announcement_id in self._active_tasks:
            self._active_tasks[announcement_id].cancel()
            del self._active_tasks[announcement_id]
    
    def _task_wrapper(self, announcement_id, task_func):
        """Thread monitoring va xotira nazorati"""
        thread = threading.current_thread()
        process = psutil.Process()
        
        try:
            while True:
                # Xotira limitini tekshirish
                memory_percent = process.memory_percent()
                if memory_percent > settings.MAX_MEMORY_PERCENT:
                    raise MemoryError(f"Memory usage too high: {memory_percent}%")
                
                # Asosiy vazifani bajarish
                task_func()
                
        except Exception as e:
            logging.error(f"Task {announcement_id} failed: {str(e)}")
            self.stop_task(announcement_id)
            raise 