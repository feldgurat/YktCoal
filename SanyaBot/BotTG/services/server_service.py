from server.server import Server


class ServerService():
    def __init__(self, server: Server):
        self.server = server
        self.urls = { 'auth': '' }

    def auth_user(self):
        auth_result = self.server.fetch(self.urls['auth'])
        return auth_result
