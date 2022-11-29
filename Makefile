
# I run this to update the database with newest papers every day or so or etc.
up:
	python3 eprint_daemon.py --num 2000
	python3 compute.py
	python3 twitter_daemon.py

# I use this to run the server
fun:
	export FLASK_APP=serve.py; flask run
