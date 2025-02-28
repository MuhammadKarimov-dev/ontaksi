import multiprocessing

# Server socket settings
bind = "unix:/var/www/ontaksi/ontaksi.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 120  # Timeoutni oshiramiz
keepalive = 5
graceful_timeout = 120

# Logging settings
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "debug"
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "taxi_site"

# Worker settings
worker_tmp_dir = "/dev/shm"
threads = 4  # Thread sonini oshiramiz

# Reload settings
reload = True
reload_engine = "auto"

# Buffer settings
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
proxy_protocol = True

# Security settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance settings
sendfile = True
preload_app = True  # Applicationni oldindan yuklash

# SSL settings (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Debug settings
spew = False
check_config = True

# Xavfsizlik
umask = 0o007
user = 'www-data'
group = 'www-data' 