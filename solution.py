import socket
import time
import requests

from bs4 import BeautifulSoup

from http_methods import HttpMethod
from http_request import HttpRequest
from task_parser import TaskParser


class Solution:
    HOST: str = "hw1.alexbers.com"
    URL: str = f"http://{HOST}"
    PORT: int = 80

    @staticmethod
    def get_response(sock: socket.socket) -> bytes:
        data = bytearray()

        while b"\r\n\r\n" not in data:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data.extend(chunk)

        header_bytes, body_bytes = data.split(b"\r\n\r\n", 1)
        headers_text = header_bytes.decode("utf-8")

        content_length = 0
        for line in headers_text.split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())
                break

        bytes_needed = content_length - len(body_bytes)

        while bytes_needed > 0:
            chunk = sock.recv(min(1024, bytes_needed))
            if not chunk:
                break
            body_bytes += chunk
            bytes_needed -= len(chunk)

        return header_bytes + b"\r\n\r\n" + body_bytes

    @staticmethod
    def solve() -> None:
        task_request = HttpRequest(Solution.HOST, "/", HttpMethod.GET)
        sock: socket.socket = socket.create_connection(
            (Solution.HOST, Solution.PORT), timeout=20
        )
        count_responses = 0
        while True:
            sock.sendall(task_request.make_request())
            response: bytes = Solution.get_response(sock)
            response_text = response.decode("utf-8")
            count_responses += 1
            print(f"Шагов сделано {count_responses}")
            if "секретный ключ" in response_text.lower():
                soup = BeautifulSoup(response_text, "html.parser")
                print(soup.find("code").text)
                break

            task = TaskParser().parse(response_text)
            task_request = HttpRequest(Solution.HOST, task.path, task.method)

            for header, value in task.headers.items():
                task_request.add_raw_header(header, value)

            for cookie, value in task.cookies.items():
                task_request.add_cookie(key=cookie, value=value)
            for param, value in task.params.items():
                task_request.add_param(param, value)
            for key, value in task.data.items():
                task_request.add_form_data(key, value)
            for key, value in task.files.items():
                task_request.add_file(key, value)

            time.sleep(0.1)

    @staticmethod
    def solve_requests() -> None:
        session: requests.Session = requests.Session()
        session.cookies.set("user", "fe3f83547d0f3cd0d7ee11b2a325ed66")
        response: requests.Response = session.get(Solution.make_url("/"))
        count_responses = 0
        while True:
            count_responses += 1
            print(f"Шагов сделано {count_responses}")
            if "секретный ключ" in (content := response.content.decode("utf-8").lower()):
                soup = BeautifulSoup(content, "html.parser")
                print(soup.find("code").text)
                break

            task = TaskParser().parse(response.content.decode("utf-8"))
            response = session.request(
                method=task.method.value,
                url=Solution.make_url(task.path),
                params=task.params,
                data=task.data,
                files={k: (k, v) for k, v in task.files.items()},
                headers=task.headers
            )

            time.sleep(0.05)

    @staticmethod
    def make_url(path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{Solution.URL}{path}"