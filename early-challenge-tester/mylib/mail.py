# my library with my own code to encode/decode, and time a part of a program
from mylib.cipher import encode, decode
from mylib.stopwatch import stopwatch
# to send emails
import smtplib # simple mail transfer protocol library
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_to_somebody(subject,body,sendtoaddrs=None):
	em_address = "@!}Kñdó@`P:=W:EoKoKWd1:=248"
	em_password = "nJK!JlV;;í!107"
	# decode email address and password
	address = decode(em_address)
	psswd = decode(em_password)
	if sendtoaddrs == None:
		sendtoaddrs = address # if not specified, send it to me
	msg = MIMEMultipart()
	msg["From"] = address
	msg["To"] = address
	msg["Subject"] = subject

	msg.attach(MIMEText(body, "plain"))

	# start server
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	# login and sendmail to myself
	try:
		server.login(address, psswd)
	except:
		raise ValueError("You must have changed your password because login failed")
	
	text = msg.as_string()
	server.sendmail(
		address, 	# email address to send msg from,
		sendtoaddrs, 	# email address to send it to
		text		# the actual stuff to send
	)
	print("Email sent to "+sendtoaddrs)
	server.quit()
