SECURITY_QUESTIONS = [
	"What was the name of your first pet?",
	"What is your favorite obstacle?",
	"How old were you when you first got the warped wall?",
	"What school did you attend in kindergarten?"
]

def question_to_id(question):
	if question not in SECURITY_QUESTIONS:
		print(f'{question} not in SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS.index(question)

def id_to_question(ID):
	if ID > len(SECURITY_QUESTIONS):
		print(f'{ID} is too big to be one of the accepted SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS[ID]
