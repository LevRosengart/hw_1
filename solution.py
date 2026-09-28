import socket

from http_methods import HttpMethod
from http_request import HttpRequest


class Solution:
    HOST: str = "hw1.alexbers.com"
    PORT: int = 80

    def solve_1(self):
        path: str = "/WbKdGlCoaHmdJbl"
        request: HttpRequest = HttpRequest(host=self.HOST, path=path, method=HttpMethod.GET)
        request.add_cookie("bC5EWiKn5wJwV3", "WBbDXqGRXzsOZpniAGDZBJ9VcFfrYFkGyffAwOnTNj")
        request_bytes: bytes = request.make_request()
        print(request_bytes)
        sock: socket.socket = socket.create_connection((self.HOST, self.PORT))
        sock.sendall(request_bytes)
        response: str = sock.recv(10240).decode()
        print(response)
        with open("response_1_1.html", "w", encoding="utf-8") as f:
            f.write(response)

Solution().solve_1()