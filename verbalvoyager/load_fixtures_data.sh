. /home/peka97/verbalvoyager/.venv/bin/activate

python3 manage.py loaddata /home/peka97/Verbal-Voyager/verbalvoyager/users/fixtures/users.json
echo "Users loaded successfully"
python3 manage.py loaddata /home/peka97/Verbal-Voyager/verbalvoyager/event_calendar/fixtures/event_calendar.json
echo "Event Calendar loaded successfully"
python3 manage.py loaddata /home/peka97/Verbal-Voyager/verbalvoyager/exercises/fixtures/exercises.json
echo "Exercises loaded successfully"
python3 manage.py loaddata /home/peka97/Verbal-Voyager/verbalvoyager/pages/fixtures/pages.json
echo "Pages loaded successfully"

