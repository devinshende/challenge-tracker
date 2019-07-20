from flask import Flask, render_template, request, redirect, url_for, flash
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, question_to_id, id_to_question
from challenges import Entry, challenges, challenge_dict
from pprint import pprint
import datetime
import ast
import os


# UNFINISHED BUSINESS FOR PERSONAL RECORDS
'''
styling of table and layout
handle bad input from users for the score field in form
'''
def read(file_name):
	with open(os.path.join('database',file_name), 'r') as file:
		x = file.read()
	try:
		return eval(x)
	except SyntaxError:
		return {}

def write(file_name, data):
	with open(os.path.join('database',file_name), 'w') as file:
		file.write(str(data))

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'jsahgfdjshgfsdjgghayfdsajhsfdayda'
# this import must be after initialization of Flask(__name__)
from views import *
if __name__ == "__main__":
	COMMENT = ''
	app.run()
