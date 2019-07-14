from datetime import datetime

def currentdatetime():
	now = datetime.now()
	months = {
		1:"January", 2:"February", 3:"March", 4:"April", 
		5:"May", 6:"June", 7:"July", 8:"August",
		9:"September", 10:"October", 11:"November", 12:"December"
	}
	mnth = months[now.month]
	day = now.day
	yr = now.year
	hr = now.hour
	min = now.minute
	if min < 10:
		min = "0"+str(min)
	hr = now.hour
	if hr > 12:
		hr -= 12
		t = f"{mnth} {day}th, {yr} {hr}:{min} PM"
	else:
		t = f"{mnth} {day}th, {yr} {hr}:{min} AM"
	return t