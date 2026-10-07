from urllib.parse import quote_plus

from http_methods import HttpMethod


class HttpRequest:
    BOUNDARY: str = "----WebKitFormBoundaryLevRosengart"

    def __init__(self, host: str, path: str, method: HttpMethod, body: bytes = b""):
        self._headers: dict[str, str] = {
            self.get_normalized_key("cookie"): "user=fe3f83547d0f3cd0d7ee11b2a325ed66",
            # self.get_normalized_key("host"): host,
        }
        self._body: bytes = body
        self._method: HttpMethod = method
        self._host: str = host
        self._path: str = path
        self._version: str = "HTTP/1.1"
        self._is_params_added: bool = False
        if self._body != b"":
            self.add_raw_header(
                key=self.get_normalized_key("content-length"),
                value=str(len(self._body)),
            )

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    def add_raw_header(self, key: str, value: str) -> None:
        if key in self._headers:
            raise ValueError("key already exists")
        self._headers[key] = value

    def add_param(self, key: str, value: str) -> None:
        if not self._is_params_added:
            self._is_params_added = True
            self._path += f"?{key}={value}"
        else:
            self._path += f"&{key}={value}"

    def make_request(self) -> bytes:
        request_start: str = f"{self._method.value} {self._path} {self._version}\r\n"
        request_headers: str = ""
        for key, value in self._headers.items():
            request_headers += f"{key}: {value}\r\n"
        request_empty_line: str = "\r\n"
        request: bytes = (request_start + request_headers + request_empty_line).encode(
            "utf-8"
        ) + self._body

        return request

    def add_form_data(self, key: str, value: str) -> None:
        content_type_key = self.get_normalized_key("content-type")
        if content_type_key not in self._headers:
            self.add_raw_header(
                key=content_type_key, value="application/x-www-form-urlencoded"
            )
        encoded_pair = f"{quote_plus(key)}={quote_plus(value)}"
        if self._body == b"":
            self._body = encoded_pair.encode("utf-8")
        else:
            self._body += f"&{encoded_pair}".encode("utf-8")
        cl_key = self.get_normalized_key("content-length")
        self._headers[cl_key] = str(len(self._body))

    def add_file(
        self, filename: str, content: str | bytes, field_name: str | None = None
    ) -> None:
        content_type_key = self.get_normalized_key("content-type")
        if content_type_key not in self._headers:
            self.add_raw_header(
                key=content_type_key,
                value=f"multipart/form-data; boundary={self.BOUNDARY}",
            )

        if field_name is None:
            field_name = filename

        content_bytes = content.encode("utf-8") if isinstance(content, str) else content

        closing_boundary = f"--{self.BOUNDARY}--\r\n".encode("utf-8")
        if self._body.endswith(closing_boundary):
            self._body = self._body[: -len(closing_boundary)]
        file_part = (
            (
                f"--{self.BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n"
            ).encode("utf-8")
            + content_bytes
            + b"\r\n"
        )

        self._body = self._body + file_part + closing_boundary

        cl_key = self.get_normalized_key("content-length")
        self._headers[cl_key] = str(len(self._body))

    def add_cookie(self, key: str, value: str) -> None:
        cookie_key = self.get_normalized_key("cookie")
        cookie_pair = f"{key}={value}"

        if cookie_key not in self._headers or not self._headers[cookie_key]:
            self._headers[cookie_key] = cookie_pair
        else:
            self._headers[cookie_key] += f"; {cookie_pair}"

    @staticmethod
    def get_normalized_key(key: str) -> str:
        return "-".join([w.capitalize() for w in key.split("-")])
