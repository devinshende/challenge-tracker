# Users should have the option to delete their account from profile-edit
- This should be in some kind of red danger box and when they click it, there should be a prompt saying "are you sure" and then ask them for their password before doing it
	- If that is accepted, then **delete the profile pic** there may be for that user with their namev by doing
	```
	if os.path.exists(user.get_profile_pic())
		os.remove(f"{user.id}.jpg")
	```
	- if that is accepted, then **delete** them from the database  using
	```
	user = User.query.get(user_id)
	db.session.delete(user)
	db.session.commit()
	```