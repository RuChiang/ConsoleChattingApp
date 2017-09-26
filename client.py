#python3

import socket
import sys
import threading
import time



#def listen(sockfd):

#def send(sockfd):


def listen(sockfd):

	
	while True:
		message = sockfd.recv(1024)
		messagestr = message.decode("ascii")

		if messagestr in ("logging out"):
			#print("return from the listener")
			return

		print(messagestr)


	
	return

def send(sockfd):

	

	global terminate	

	#print(terminate)
	
	while True:
		message = input("")
		sockfd.send(message.encode("ascii"))
		if message == "logout":
			#print("return from sender")
			return
	return


def main(argv):

	login = False

	loginTime = 0

	if len(argv) == 3:
		ip = sys.argv[1]
		port = int(sys.argv[2])
	else:
		print("Invalid Input. client.py <connecting_IP> <connecting_port>")
		sys.exit()

	sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sockfd.connect((ip,port))

	message = sockfd.recv(1024)	#"Please input your username and password" or account blocked due to invalid ID input

	messagestr = message.decode("ascii")

	print(messagestr)

	if messagestr in ('Your account is blocked due to invalid ID input. Please try again later'):
		sockfd.close()
		sys.exit()
		

	while login == False :

		userid = input("ID: ")

		password = input('Password: ')

		credentials = userid + ' '  + password

		sockfd.send(credentials.encode("ascii"))

		loginmsg = sockfd.recv(1024)
	
		loginstr = loginmsg.decode("ascii")
	
		print(loginstr)

		if loginstr == 'welcome to this messaging application':
			
			while True:
				#open 2 threads	
				cname = userid + ' listen' 
				thd = threading.Thread(name =cname, target = listen, args=(sockfd,) )
				thd.start()
				cname = userid + ' send'
				thd = threading.Thread(name = cname, target = send, args=(sockfd,))
				thd.start()
				
				sys.exit()


#problem to work on: how to terminate the client side
		elif loginstr in( 'Invalid password. Your account has been blocked. Please try again later', 'Your account is blocked due to multiple login failures. Please try again later', 'Invalid ID'): 
			sockfd.close()
			sys.exit()

	
	sockfd.close()


if __name__ == '__main__':
	main(sys.argv)
