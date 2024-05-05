#!/bin/bash
source /home/peka97/verbalvoyager/.venv/bin/activate
exec gunicorn -c "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/guni_config.py" --error-logfile "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/guni-error.log" --access-logfile "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/guni-access.log"  verbalvoyager.wsgi