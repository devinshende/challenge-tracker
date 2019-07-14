# challenge-tracker
Website to track challenge times for obstacles at nwninjapark in springfield, OR

# usage
```
git clone <this repo>
cd challenge-tracker
pip install virtualenv
pip install Flask
virtualenv venv
source venv/bin/activate
python app.py
``` 
On some computers virtualenv that way doesn't work. This is what worked for me
```
git clone <this repo>
cd challenge-tracker
pip install virtualenv
pip install Flask
python3 -m virtualenv venv
source venv/bin/activate.csh
python3 app.py
```
open localhost:5000 in a browser
