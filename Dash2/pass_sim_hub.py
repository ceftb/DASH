import world_hub
import utils

class ServiceHub(WorldHub):
	def __init__(self):
		self.serviceList = {}	# predefined dictionary service_name:service
		self.serviceDist = {}	# predefined distribution list serv_type:distribution
		self.knownUsernames = {}	# dictionary service_name:[usernames]

		self.serviceBase = {}	# dictionary service_name:[(username, password)]
		self.serviceStatus = {}	# dictionary service_name:[username, bool]

	def createServeClientThread(self, (client, address)):
		return ServiceServeClientThread((client, address), self)
	# API for password sim


class ServiceServeClientThread(serveClientThread):
	def __init__(self, (client, address), service_hub):
		ServiceClientThread.__init__(self, (client, address))
		self.service_hub = service_hub


	def processSendActionRequest(self, id, action, aux_data):
		print "Processing Action ", action, aux_data

		if action == 'getAccount':
			service_type = aux_data[0]
			return distPicker(self.service_hub.serviceDist[service_type], random.random())

		elif action == 'createAccount':
			service = aux_data[0]
			username = aux_data[1]
			password = aux_data[2]
			requirements = self.service_hub.serviceList[service].getRequirements()
			if username in self.knownUsernames[service]:
				print "Failed: username already exists"
				return('failed:user', [])

			if requirements.verify(username, password):
				print 'Success: account successfully created on ', service
				self.service_hub.knownUsernames[service].append(username)
				self.service_hub.serviceBase[service].append((username, password))
				return('success', [])
			else:
				print "Failed: password doesn't meet the requirements"
				return('failed:reqs', [requirements])

		elif action == 'signIn':
			service = aux_data[0]
			username = aux_data[1]
			password = aux_data[2]
			if (username, password) in self.serviceBase[service]:
				if (username, true) in self.serviceStatus[service]
					print "user logged in successfully to ", service
					return ('success', [])
				else:
					print "user already logged in, sign out first"
					return ('failed:logged_in', [])
			else:
				print "user failed to log in"
				return ('failed:unknown_password', [])
		elif action == 'retrieveStatus':
			service = aux_data[0]
			username = aux_data[1]
			if (username, True) in self.service_hub.serviceStatus[service]:
				self.service_hub.serviceStatus[service].remove((username, True))
				return ('success', [])
			else:
				return ('failure', [])

if __name__ == "__main__":
    ServiceHub().run()
