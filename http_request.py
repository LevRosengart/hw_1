from http_methods import HttpMethod


class HttpRequest:
    def __init__(self, host: str, path: str, method: HttpMethod, body: bytes = b""):
        self._headers: dict[str, str] = {
            self.get_normalized_key("cookie"): "user=fe3f83547d0f3cd0d7ee11b2a325ed66",
        }
        self._body: bytes = body
        self._method: HttpMethod = method
        self._host: str = host
        self._path: str = path
        self._version: str = "HTTP/1.1"
        if self._body != b"":
            self.add_raw_header(key=self.get_normalized_key("content-length"), value=str(len(self._body)))

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    def add_raw_header(self, key: str, value: str) -> None:
        if key in self._headers:
            raise ValueError("key already exists")
        self._headers[key] = value

    def make_request(self) -> bytes:
        request_start: str = f"{self._method.value} {self._path} {self._version}\r\n"
        request_headers: str = ""
        for key, value in self._headers.items():
            request_headers += f"{key}: {value}\r\n"
        request_empty_line: str = "\r\n"
        request: bytes = (
            request_start + request_headers + request_empty_line
        ).encode() + self._body

        return request

    def add_cookie(self, key: str, value: str) -> None:
        if self.get_normalized_key("cookie") not in self._headers:
            self._headers[self.get_normalized_key("cookie")] = value
        else:
            self._headers[self.get_normalized_key("cookie")] += f"; {key}={value}"

    @staticmethod
    def get_normalized_key(key: str) -> str:
        return "-".join([w.capitalize() for w in key.split("-")])