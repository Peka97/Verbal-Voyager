command = '/home/peka97/verbalvoyager/.venv/bin/gunicorn'
pythonpath = '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager'
bind = '127.0.0.1:8001'
workers = 3
errorlog = "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/guni-error.log"
loglevel = 'warning'
accesslog = "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/guni-access.log"
access_log_format = '%(t)s %(h)s %(l)s %(u)s "%(r)s" | %(s)s | %(b)s "%(f)s" "%(a)s"'
user = 'peka97'
limit_requests_fields = '32000'
limit_requests_field_size = '0'
raw_env = 'DJANGO_SETTINGS_MODULE=verbalvoyager.settings'
