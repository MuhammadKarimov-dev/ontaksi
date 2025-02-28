import multiprocessing

# Server socket settings
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Timeout settings
timeout = 120  # Increase timeout to 120 seconds
keepalive = 5
worker_connections = 1000

# Logging settings
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "taxi_site"

# SSL settings (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Worker settings
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# Reload settings
reload = True
reload_engine = "auto"

capture_output = True 