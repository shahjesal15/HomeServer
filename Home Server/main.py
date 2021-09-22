import socket
import threading
import pickle
import signal
import sys
import gzip

class Server:
	def __init__(self):
		# SERVER CONTROL FLAGS
		self.running = True

		# SERVER
		PORT = 80
		SERVER = socket.gethostbyname(socket.gethostname())		 
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# REUSING SOCKETS
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# BINDING SERVER
		self.server.bind((SERVER, PORT))
		print(' [*] server running on {}:{}'.format(SERVER, PORT))

		# TIMING OUT SERVER
		self.server.settimeout(0.8)


		# LISTENING TO CLIENTS
		self.server.listen(4)

		# TRACKING CLIENTS THREADS
		self.clients = []

	# MAIN FUNCTION
	def run(self):
		client, addr = None, None
		# SERVER LOOP
		while self.running:
			try:
				client, addr = self.server.accept()
			except socket.timeout:
				client, addr = None, None
			if client is not None:
				clientThread = threading.Thread(target=self.clientHandler, args=(client,addr,))
				self.clients.append((clientThread, client))
				clientThread.start()
				print(' [*] connected to {}:{}'.format(addr[0], addr[1]))

	# HANDLING CLIENTS
	def clientHandler(self, client, addr):
		response = ''
		file = 'Database\\index.html'
		type = ''
		header = 'HTTP/1.0 200 OK\nContent-Type: {}\nContent-Length: {}\nConnection: Keep-alive\n\n'
		with open(file, 'rb') as index:
			response = index.read()
		response = (header.format('text/html', len(response))).encode('utf-8') + response
		client.sendall(response)
		print(' [?] requested fulfilled for {}:{}'.format(addr[0], addr[1]))
		client.close()

	# SIGNAL CALLBACK
	def _exit(self, signal, handler):
		self.running = False
		for client_tuple in self.clients:
			clientThread, client = client_tuple
			client.close()
			clientThread.join()
		print(' [x] server stopped running...')
		sys.exit(0)

server = Server()
print(' [>] CTRL + C to stop service...')
signal.signal(signal.SIGINT, server._exit)
server.run()