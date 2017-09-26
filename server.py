#python3

import socket
import sys
import threading
import re
import time
import datetime
import signal

def broadcast(sockfd,id, message):
	f =0 
	notToSend = []
	sendSoc = []

	for i in blockList:		#check who blocked id, and put them to notToSend list
		if i.split()[1] == id:
			notToSend.append(i.split()[0])

	for i in usersock:
		if i.split()[0] not in notToSend:
			sendSoc.append(i.partition(' ')[2])


	for user in socketList:
		if str(user) in sendSoc: 
			if user!= sockfd:
				user.send(message.encode("ascii"))
		else:
			f = 1
	if f==1:
		message = "Your message could not be delivered to some recipients"
		sockfd.send(message.encode("ascii"))
		
	
	return

def brologinout (sockfd,id, message):
	notToSend = []
	sendSoc = []

	for i in blockList:		#check who blocked id, and put them to notToSend list
		if i.split()[0] == id:
			notToSend.append(i.split()[1])

	for i in usersock:
		if i.split()[0] not in notToSend:
			sendSoc.append(i.partition(' ')[2])


	for user in socketList:
		if str(user) in sendSoc: 
			if user!= sockfd:
				user.send(message.encode("ascii"))

	return






def afterlogin(sockfd, id, loginrec):
	
	commandstr = "login"	
	broadmsg = id + " logged in"
	brologinout(sockfd, id, broadmsg)


	
	global loginList
	global socketList
	global usersock
	global offline
	global blockList
	global Ulogout
	global UlogoutTime

	
	for i in offline:
		if i.split()[1] == id:
			#print(i.partition(',')[0])
			#print(i.partition(',')[2])
			offmsg =  i.partition(',')[2]
			sockfd.send(offmsg.encode("ascii"))
		
	
	while True:		#listening to all sort of commands

#receiving command
		command = sockfd.recv(1024)
		commandstr = command.decode("ascii")		


#whoelse
		if commandstr.split()[0] == "whoelse" and len(commandstr.split()) == 1:
			for user in loginList:
				if user.split()[0] != id: 
					sendm = (user.split()[0])
					sockfd.send(sendm.encode("ascii"))
					time.sleep(0.01)

#whoelsesince
		elif commandstr.split()[0] == "whoelsesince" and len(commandstr.split()) == 2:
			n = -1
			t = datetime.datetime.now()
			folks = []
			for user in UlogoutTime:

				td= t-user
				k =  td.seconds + td.microseconds/1000000 
				#print(k)
				n = n + 1
				#print("now: ",t)
				#print("user logout time:", Ulogout[n], user)
				#print("t-user: ",k)
				if float(commandstr.split()[1]) >= k and Ulogout[n] not in folks and Ulogout[n] != id:
					folks.append(Ulogout[n])
			for k in loginList:
				if k.split()[0] not in folks and k.split()[0] != id:
					message = k.split()[0]
					sockfd.send(message.encode("ascii"))
					time.sleep(0.01)
			for user in folks:
					message = user
					sockfd.send(message.encode("ascii"))
					time.sleep(0.01)

#logout
		elif commandstr == "logout" and len(commandstr.split()) == 1:
			loginList.remove(loginrec)
			socketList.remove( sockfd)
			usersock.remove(id + ' ' + str(sockfd))
			broadmsg = id + " logged out"
			brologinout(sockfd, id, broadmsg)
			t = datetime.datetime.now()
			UlogoutTime.append(t)
			Ulogout.append(id)
			message = "logging out" 
			sockfd.send(message.encode("ascii"))
			#print("logout time: ",id, ' ',datetime.datetime.now())
			return

#broadcast
		elif commandstr.split()[0] == "broadcast" and len(commandstr.split()) >= 2:
			broadmsg = id + ': ' + commandstr.partition(' ')[2]
			#print(broadmsg)
			broadcast(sockfd, id, broadmsg)

#message(offline not included for now)
		elif commandstr.split()[0] == "message" and len(commandstr.split()) >= 2:

			if commandstr.split()[1] == id:
				message = "Error. Cannot message self"
				sockfd.send(message.encode("ascii"))	


			elif commandstr.split()[1]  in checkId:	#check if the user exists
				name = commandstr.split()[1]
				intermessage = commandstr.partition(' ')[2]
				message = id + ': ' + intermessage.partition(' ')[2]
				loginlist = [words for segments in loginList for words in segments.split()]
				if name in loginlist:		#if the user is logged in
					if (name + ' ' + id) not in blockList:	#check if the id is block by name
						for user in usersock:
							if user.split()[0] == name:
								for k in socketList:
									if user.partition(' ')[2] == str(k):
										k.send(message.encode("ascii"))
					else:
						message = "Your message cannot be delivered as the recipient has blocked you"
						sockfd.send(message.encode("ascii"))
					
				else:
					offmsg = id + " " + commandstr.split()[1] + " ," + message
					offline.append(offmsg)
					#sockfd.send(message.encode("ascii"))

			else:
				message = "Error. Invalid user"
				sockfd.send(message.encode("ascii"))

#block
		elif commandstr.split()[0] == "block" and len(commandstr.split()) == 2:
			if commandstr.split()[1] == id:
				message = "Error. Cannot block self" 
				sockfd.send(message.encode("ascii"))
			elif commandstr.split()[1] not in checkId:
				message = "Error. User is invalid" 
				sockfd.send(message.encode("ascii"))
			elif id + ' ' + commandstr.split()[1] in blockList:
				message = commandstr.split()[1] + " is blocked already"
				sockfd.send(message.encode("ascii"))
			else:		#append to block list
				blockList.append(id + ' ' + commandstr.split()[1])
				message = commandstr.split()[1] + " is blocked" 
				sockfd.send((message).encode("ascii"))
				
#unblock
		elif commandstr.split()[0] == "unblock" and len(commandstr.split()) == 2:
			if commandstr.split()[1] == id:
				message = "Error. Cannot unblock self" 
				sockfd.send(message.encode("ascii"))
			elif commandstr.split()[1] not in checkId:
				message = "Error. User is invalid" 
				sockfd.send(message.encode("ascii"))
			elif (id + ' ' + commandstr.split()[1]) not in blockList:
				message = "Error. " + commandstr.split()[1] + " was not blocked"
				sockfd.send(message.encode("ascii"))
			else:
				blockList.remove(id + ' ' + commandstr.split()[1])
				message = commandstr.split()[1] + " is unblocked" 
				sockfd.send((message).encode("ascii"))
				

				
			


		else:
			message = "Error. Invalid command"			
			sockfd.send(message.encode("ascii"))

	return



def client_thd(sockfd):
	#print("thread created")

	if userIP in IPBlock:
		errmsg = "Your account is blocked due to invalid ID input. Please try again later"
		sockfd.send(errmsg.encode("ascii"))
		return

#user authentication
	login = False

	loginTime = 0

#checkcredentials
	with open("credentials.txt") as f:
		content = f.readlines()
	content = [x.strip() for x in content]



#checkId
	global checkId
	f = open("credentials.txt", "r")
	lines = f.readlines()
	checkId = []
	for x in lines:
		checkId.append(x.split(' ')[0])
	f.close()

	
	msg = "Please input your username and password"	
	sockfd.send(msg.encode("ascii"))


	while login == False :

		credentials = sockfd.recv(1024)

		credentialsstr = credentials.decode("ascii")
		
		global onhold 

		global loginList

		global socketList

		global usersock

		global UlogoutTime
		
		global Ulogout


		#print(credentialsstr)
		

		if credentialsstr.split()[0] in checkId:		#valid user ID

			if credentialsstr.split()[0] in onhold:
				loginmsg = "Your account is blocked due to multiple login failures. Please try again later"
				sockfd.send(loginmsg.encode("ascii"))
				break;

			elif (credentialsstr.split()[0] + ' ' + userIP) in loginList:
				loginmsg = "The user is logged in already"
				sockfd.send(loginmsg.encode("ascii"))

			else:
				if credentialsstr in content:
					login = True
					loginmsg = "welcome to this messaging application"
					t = datetime.datetime.now()
					loginrec = credentialsstr.split()[0] + ' ' + userIP
					usoc = credentialsstr.split()[0] + ' ' + str(sockfd)
					loginList.append(loginrec)
					socketList.append(sockfd)
					usersock.append(usoc)
					#print(loginrec)
					sockfd.send(loginmsg.encode("ascii"))
					time.sleep(0.01)
					afterlogin(sockfd, credentialsstr.split()[0],loginrec)

				else:
					loginTime = loginTime + 1

					if loginTime == 3:
						loginmsg = "Invalid password. Your account has been blocked. Please try again later"
						sockfd.send(loginmsg.encode("ascii"))
						onhold.append(credentialsstr.split()[0])
						time.sleep(block_duration)
						onhold.remove(credentialsstr.split()[0])
						break;

					else:
						loginmsg = "Invalid password"	
						sockfd.send(loginmsg.encode("ascii"))	

	
		else:
			loginmsg = "Invalid ID"
			sockfd.send(loginmsg.encode("ascii"))	
			IPBlock.append(userIP)
			time.sleep(block_duration)
			IPBlock.remove(userIP)
			break
			

	

#
#	

	return

onhold = [] #store username which have 3 failed attempted in password
IPBlock = []  #store ip which enters the wrong ID
loginList = [] #store 'ID' + IPs
socketList = [] #store the real sockets 
checkId = [] #list with IDs
timeout = 0
block_duration = 0
userIP = ""
usersock = [] #store 'ID' + 'str(socket)'
offline = [] # store 'sender' + ' ' + 'receiver' + ' ,' +'message'
blockList = [] #store 'blockid' + ' ' + 'blockedid'
UlogoutTime = [] #store datetime
Ulogout = []# store userid



def main(argv):

	global userIP

	if len(argv) == 4:
		port = int(argv[1])
		global block_duration
		block_duration = int(argv[2])
		global timeout 
		timeout = int(argv[3])
	else:
		print("Invalid Input. server.py <server_port> <block_duration> <timeout>")
		sys.exit()



	#print("this is timeout %d" %timeout)

	sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	try:
		sockfd.bind(("",port))
	except socket.error as emsg:
		print("Socket bind error: ", emsg)
		sys.exit(1)

	#print("server is on")


	sockfd.listen(15)

	cthread = []



#	print("start the monitor thread")	
#	mthd = threading.Thread(name = "Monitor", target = monitor_thd)
#	mthd.start()

#	cthread.append(mthd)
	
	while True:
		try:
			new, who = sockfd.accept()
			userIP = who[0]
			#print("this is whos ip", who[0])
			##print(new)

			#print("a new client has arrived ", who)
			cname = who[0] + ':' + str(who[1])
			thd = threading.Thread(name = cname, target = client_thd, args=(new, ))
			thd.start()
			cthread.append(thd)


		except	 KeyboardInterrupt:
			print("at main, caught by the keyboard")	
			break;



	new.close()
	sockfd.close()

if __name__ == '__main__':
	main(sys.argv)

