# challenge-tracker
Website to track challenge times for obstacles at nwninjapark in springfield, OR

# usage
```
git clone <this repo>
cd challenge-tracker
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install Flask
python app.py runserver
``` 
On some computers virtualenv that way doesn't work. This is what worked for me
```
git clone <this repo>
cd challenge-tracker
pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate.csh
pip install Flask
python3 app.py runserver
```
open localhost:5000 in a browser
