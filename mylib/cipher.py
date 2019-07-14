#V2 goal: extended support for new characters:
# Capital letters, 
# numbers 
# and punctuation (except space_chars) 
# allowed as opposed to just lowercase letters. 
import random
# characters = (
# 	"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", 
# 	# letters
# 	"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
# 	# uppercase letters
# 	"`","0","1", "2", "3", "4", "5", "6", "7", "8", "9",
# 	#numbers
# 	'~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', ';', ':', '\'', '"', ',', '<', '.', '>', '/', '?'
# 	# punctuation
# )
characters = (
'w', 't', 'F', '7', 'H', 'q', '.', '!', '$', '=', '~', '[', 'v', 'I', 'R', 
'5', 'm', 'e', 'n', '%', 'N', 'j', '(', 'r', ']', '#', 'g', '6', 'S', 'Z', 
'T', 'u', 'U', '^', 'K', ';', 'c', ',', '&', 'L', '1', 'B', '-', '_', '@', 
':', 'W', 'X', 'G', 'A', 's', 'y', 'i', 'Y', '`', '0', '+', 'h', '*', '2', 
'x', 'C', 'Q', 'O', '}', 'k', 'a', 'J', 'V', 'l', 'M', '>', 'P', ')', '3', 
'<', '?', '/', 'o', 'p', 'd', '"', '9', 'z', 'D', 'E', '8', '{', '4', 'b', 
'f', "'", 'é', 'ú', 'ó','í', 'á', 'ñ', '¿'
)

# SUPPORTED CHARS		abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890 ~!@#$%^&*()-=_+[]{};':",./<>?áéíóúñ¿
# UNSUPPORTED CHARS		|\ SPACE

space_chars = ['|', 'å', 'ƒ', '∆', ' '] # what a space can be turned into. MUST NOT BE IN CHARACTERS

listlen = len(characters) 
maxindex = listlen-1 


def encode(message, printing=False):
	if message == '': 
		return '' #don't give them any clues by giving the encoded adder when they encode nothing. Instead, return nothing.
		
	adder = random.randint(2,maxindex) # how many letters right to shift in the characters
	
	if printing not in ["True", "yes", "YES", "PRINT", 'print', 'true', 't', 'y', 0, True]:
		printing = False
		#This makes it so that by default, nothing is printed (to keep it secret). This bypasses truthiness and falsiness to define when it should print
	
	if printing:
		print("alphabet is ")
		print("\n\nTHE ORIGINAL MESSAGE IS:")
		print(message, "\n\n")
		print("ADDER:\t",adder,"\n\n")
	msg = ""
	for char in message:
		if printing:
			print("(CHARACTER:", char, ")")
		if char in characters:
			char_index = characters.index(char)
			coded_index = char_index + adder # add 5 or whatever to char_index
			if coded_index <= maxindex:
				#less than or equal to maxindex, we're all good.
				coded_char = characters[coded_index]
				if printing:
					print(coded_index, "is less than or equal to",maxindex)
			elif coded_index > maxindex:
				#greater than maxindex, subtract listlen to wrap back around.
				if printing:
					print(coded_index,"is greater than",maxindex)
				coded_index = coded_index - listlen
				coded_char = characters[coded_index]
				
			else:
				#If you see this printed, then that means someone messed with characters so that it is more than just letters a-z
				print('\n\n\nI can\'t deal with that. ', coded_index,
					  ' is too big')
				print("DID SOMEONE MESS WITH THE TUPLE characters ON LINE 5?\n\n\n")
				coded_char = ''
	
		elif char == " ":
			# these are all the possible codes for a space.
			coded_char = random.choice(space_chars) # if it's a space, code it as one of these /+=\
			if printing:
				print("space")

		else:  # not in my characters and not a space
			if printing:
				print("\tThe character ", char,
					  "is not in my alphabet! I will not include it in the message.\n")
			else:
				print("\tThat character is not in my alphabet! I will not include it in the message.")
			coded_char = ""
		
		if coded_char in ["'",'"']: # if it is a double or single quote, then add a backslash so python doesn't think the string has ended
			coded_char += "\\" # put it at the end so that when the message is reversed, it will be in front "\""
			if printing:
				print("Backslash added to coded_char")
		if printing:
			print('coded char is "',coded_char,'"\n')
		
		msg = msg + coded_char

	msg = msg[::-1] # reverse it
	#after message, add 3 characters. the two important ones are at index -1 and -3. They are the adder
	# the one at index -2 is a dummy number from 0-9
	# a1, randnum, a2
	randnum = random.randint(0,9)
	if adder < 10:
		a1 = "0"
		a2 = str(adder)[0]
	elif adder >= 10:
		a1 = str(adder)[0]
		a2 = str(adder)[1]
	msg = msg + a1 + str(randnum) + a2
	
	if printing:
		print("\nTHE CODED MESSAGE IS:")
		print(msg, "\n\n")
	return msg
	
	#END OF ENCODER FUNCTION
	
def decode(message, printing=False):
	if message == '':
		return ''
	if printing not in ["True", "yes", "YES", "PRINT", 'print', 'true', 't', 'y', 0, True]:
		printing = False
		#This makes it so that by default, nothing is printed (to keep it secret). This bypasses truthiness and falsiness to define when it should print
	if printing:
		print("\n\nTHE ENCODED MESSAGE IS:")
		print(message, "\n\n\n")
	msg = ""
	
	coded_adder = message[-3:]
	message = list(message) # must be a list to delete last 3 characters from the end
	del message[-3:]
	m = ""
	for i in message:
		m += i
	message = m
	
	if str(coded_adder)[0] == 0:
		# if the first char is 0, then adder is just the last char
		adder = int(coded_adder[2])
	else:
		# if the first char is not 0, then adder is the numbers at -3 and -1
		adder = int(coded_adder[0] + coded_adder[2]) 
	message = message[::-1] # reverse it back
	# done interpreting messiness of message, now we can take it char at a time
	if printing:
		print("Characters have been put in order and are ready to be decoded one at a time.\ncurrent message is:\n",message,"\n\n")
	for char in message:
		if printing:
			print("(CHARACTER:", char, ")")
		if char in characters:
			char_index = characters.index(char)
			decoded_index = char_index - adder

			if decoded_index >= adder:
				# more than or equal to 5, we're all good to subtract 5
				decoded_char = characters[decoded_index]
				if printing:
					print(decoded_index, "is greater than or equal to",adder)
					
			elif decoded_index >= 0-adder and decoded_index < adder:
				#more than -5 (or whatever adder is), less than 0, then add 5 (or whatever adder is) to get the decoded char
				decoded_index += listlen
				if decoded_index > maxindex:
					decoded_index -= listlen #if it would get an index out of range error, just undo the added listlen
				decoded_char = characters[decoded_index]
					
				if printing:
					print(char_index,"is less than 0")
	
		elif char in space_chars:
			# these are all the possible codes for a space.
			decoded_char = " "
			if printing:
				print("space")
		elif char == "\\":
			if printing:
				print("backslash; not important to message")
			decoded_char = ''
		else:  # not in my characters if it's not in characters, not a space, and not a backslash
			if printing:
				print("\tThe character ", char, '''is not in my characters! I cannot decode it. 
				MAKE SURE THAT YOU HAVE A CORRECT CODE TO RUN THIS FUNCTION''')
			else:
				print("\tThat character is not in my characters! I cannot include it")
				decoded_char = ""
		if printing:
			print('decoded char is "',decoded_char,'"\n')
		msg = msg + decoded_char
	if printing:
		print("\nTHE DECODED MESSAGE IS:")
		print(msg, "\n\n")
	return msg

if __name__ == "__main__":
	import time
	choice = ""
	while True:
		time.sleep(0.3)
		print("\nWhat would you like to do?")
		print("  1. encode a message")
		print("  2. decode a message")
		print("  3. quit")
		choice = input().lower()

		if choice == "1" or choice == "e":
			msg = input("What would you like to encode?\n")
			x = encode(msg,False)
			print("\nENCODED MESSAGE:\n",x)
		elif choice == "2" or choice == "d":
			msg = input("What would you like to decode?\n")
			y = decode(msg,False)
			print("\nDECODED MESSAGE:\n",y)
		elif choice == "3" or choice.lower() in ["quit","q","stop","end","terminate"]:
			print("Quitting...")
			time.sleep(0.8) # I know, artificial wait. But it looks nice
			break
		else:
			print("\nPlease type 1, 2, or 3 to pick an action")
			time.sleep(0.7)
		# msg = input("what should I encode?\n ")
		# x = encode(msg,input("\nshould I print debugger statements for encoder?\n"))
		# print("\nENCODED MESSAGE:\n",x,"\ntime to decode it...\n")
		# y = decode(x,input("\nshould I print debugger statements for decoder?\n"))
		# print("\nDECODED MESSAGE:\n",y)
		#print("\n\nCOMPARE ORIGINAL TO DECODED OF ENCODED OF ORIGINAL\n",msg,"\n",y)

	
#LAST EDITED JULY 21 2018