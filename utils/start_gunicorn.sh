#!/bin/bash
source /home/peka97/verbalvoyager/.venv/bin/activate
exec gunicorn -c "/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/guni_config.py" verbalvoyager.wsgi