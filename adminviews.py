from views import *

@app.route('/siteadmin/',methods=['GET','POST'])
def siteadmin():
	# from app import get_admin_auth, write_admin_auth
	# if request.method == 'POST':
	# 	print('logging out')
	# 	write_admin_auth(False)
	# 	return redirect('/')
	# if get_admin_auth():
	return render_template('siteadmin/admin.html',scnum=len(Suggestion.query.all()))
	# else:
		# flash('please sign in here and then return to siteadmin')
		# return redirect('/admin')

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
		suggestion_to_accept = request.form.get('suggestion')
		if verbose: print('accepting ',suggestion_to_accept)
		s = Suggestion.query.filter_by(name=suggestion_to_accept).first()
		print(f'accepting {repr(s)} = {s}')
		print({'type':s.type,'name':suggestion_to_accept})
		t = s.type.lower()
		if t == 'reps':
			t = 'reps'
		add_challenge({'type':t,'name':suggestion_to_accept})
		# once it has been added, delete it from suggestions
		db.session.delete(s)
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
		s = Suggestion.query.filter_by(name=suggestion_to_delete).first()
		print(f'deleting {repr(s)} = {s}')
		db.session.delete(s)
		db.session.commit()
		return redirect('/siteadmin/challenges')
	return render_template('siteadmin/challenges/delete.html',json=Suggestion.query.all())

@app.route('/siteadmin/challenges/delete-ch', methods=['GET','POST'])
def admin_delete_ch():
	from constants import challenge_dict
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
