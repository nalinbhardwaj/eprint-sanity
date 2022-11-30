
# I run this to update the database with newest papers every day or so or etc.
up:
	python3 eprint_daemon.py --num 2000
	python3 compute.py
	python3 twitter_daemon.py

fun_prod:
	gunicorn -w 4 'serve:app' --daemon --bind 0.0.0.0:8000