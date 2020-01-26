from views import *

@app.route('/siteadmin/challenges')
def challenge_suggestions():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')
	return render_template('siteadmin/challenges/challenge.html',json=Suggestion.query.all())

@app.route('/siteadmin/challenges/accept', methods=['GET','POST'])
def admin_accept():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')

	if request.method == 'POST':
		suggestion_to_accept = str(request.form.get('suggestion'))
		if verbose: print('accepting ',suggestion_to_accept)
		suggestion = Suggestion.query.filter_by(name=suggestion_to_accept).first()
		assert suggestion
		s_type = suggestion.type.lower()
		assert s_type in dir(ChallengeTypes), "The suggested type is not a valid type"
		add_challenge({'type':s_type,'name':suggestion_to_accept})
		# once it has been added, delete it from suggestions
		db.session.delete(suggestion)
		db.session.commit()
		return redirect('/siteadmin/challenges')
	return render_template('siteadmin/challenges/accept.html',json=Suggestion.query.all())

@app.route('/siteadmin/challenges/delete', methods=['GET','POST'])
def admin_delete():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')

	if request.method == 'POST':
		suggestion_to_delete = request.form.get('suggestion') 
		if verbose: print('deleting the suggestion',suggestion_to_delete)
		suggestion = Suggestion.query.filter_by(name=suggestion_to_delete).first()
		print(f'deleting {repr(suggestion)} from db')
		db.session.delete(suggestion)
		db.session.commit()
		return redirect('/siteadmin/challenges')
	return render_template('siteadmin/challenges/delete.html',json=Suggestion.query.all())

@app.route('/siteadmin/challenges/delete-ch', methods=['GET','POST'])
def admin_delete_ch():
	from constants import load_challenge_dict
	challenge_dict = load_challenge_dict()
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')

	if request.method == 'POST':
		ch_to_delete = request.form.get('challenge') 
		if verbose: print('deleting the challenge',ch_to_delete)
		print('old challenge_dict\n\n',challenge_dict)
		for lst in challenge_dict.values():
			for item in lst:
				print(item)
				if item == ch_to_delete:
					print('yay')
					lst.remove(item)
		with open('database/challenges.json','w') as file:
			file.write(json.dumps(challenge_dict))
		print('new challenge_dict:\n\n')
		print(challenge_dict)
		delete_all_of_ch(ch_to_delete)
		return redirect('/siteadmin/challenges')
	return render_template('siteadmin/challenges/delete-ch.html',
		json=Suggestion.query.all(),
		challenge_dict=challenge_dict)

@app.route('/siteadmin/securityq')
def security_questions():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')

	from constants import load_security_questions
	SECURITY_QUESTIONS = load_security_questions()
	return render_template('siteadmin/questions/securityq.html',SECURITY_QUESTIONS=SECURITY_QUESTIONS)

@app.route('/siteadmin/securityq/add',methods=['GET','POST'])
def security_question_add():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')

	from constants import load_security_questions
	SECURITY_QUESTIONS = load_security_questions()
	if request.method == 'POST':
		q = request.form.get('question')
		if limit_input_size(name=q, max_size=100, item="security question"):
			return redirect('/siteadmin/securityq/add')
		add_security_question(q)
		return redirect('/siteadmin/securityq')
	return render_template('siteadmin/questions/add.html',SECURITY_QUESTIONS=SECURITY_QUESTIONS, add=True)
 
@app.route('/siteadmin/securityq/remove',methods=['GET','POST'])
def security_question_remove():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to siteadmin')
		return redirect('/admin')
		
	from constants import load_security_questions
	SECURITY_QUESTIONS = load_security_questions()
	if request.method == 'POST':
		q = request.form.get('question')
		status = remove_security_question(q)
		if status == False:
			flash('You cannot delete that security question because it is already in use by somebody')
		return redirect('/siteadmin/securityq')
	return render_template('siteadmin/questions/remove.html',SECURITY_QUESTIONS=SECURITY_QUESTIONS, remove=True)

@app.route('/siteadmin/img')
def imgview():
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to /siteadmin/img')
		return redirect('/admin')
	users = User.query.all()
	return render_template('siteadmin/img.html',users=users)

@app.route('/siteadmin/<username>/')
def userview(username):
	from app import get_admin_auth
	if not get_admin_auth():
		flash('please sign in here and then return to that page')
		return redirect('/admin')

	user = User.query.filter_by(username=username).first()
	ch = json_to_objects(user.challenges)
	return render_template('siteadmin/user.html',user=user,ch=ch)

