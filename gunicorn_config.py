import multiprocessing

# Server socket settings
bind = "unix:/var/www/ontaksi/ontaksi.sock"  # Unix socket ishlatamiz
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Timeout settings
timeout = 120  # Increase timeout to 120 seconds
keepalive = 5
worker_connections = 1000

# Logging settings
accesslog = "/var/log/ontaksi/access.log"
errorlog = "/var/log/ontaksi/error.log"
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

# Xavfsizlik
umask = 0o007
user = 'www-data'
group = 'www-data'

capture_output = True 