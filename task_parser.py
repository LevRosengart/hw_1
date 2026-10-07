from dataclasses import dataclass, field
from bs4 import BeautifulSoup

from http_methods import HttpMethod


@dataclass
class ParsedTask:
    method: HttpMethod = HttpMethod.GET
    path: str = ""
    params: dict = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    files: dict = field(default_factory=dict)


class TaskParser:
    @classmethod
    def parse(cls, raw_response: str) -> ParsedTask:
        if "\r\n\r\n" in raw_response:
            raw_response = raw_response.split("\r\n\r\n", 1)[1]

        soup = BeautifulSoup(raw_response, "html.parser")
        result = ParsedTask()

        body_text = (soup.body.get_text() if soup.body else soup.get_text()).lower()
        if "post-запрос" in body_text or "загрузите файл" in body_text:
            result.method = HttpMethod.POST
        elif "get-запрос" in body_text:
            result.method = HttpMethod.GET

        link_tag = soup.find("a", href=True)
        if link_tag:
            result.path = link_tag["href"]
        else:
            code_tag = soup.find("code")
            if code_tag and code_tag.text.startswith("/"):
                result.path = code_tag.text.strip()

        tables = soup.find_all("table")
        for table in tables:
            prev_text = table.previous.text.strip()
            table_data = {}
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                if len(cols) == 2 and cols[0].name == "td":
                    key = cols[0].text.strip()
                    val = cols[1].text.strip()
                    table_data[key] = val

            if "файл" in prev_text:
                result.files = table_data
            if "параметр" in prev_text:
                result.params = table_data
            elif "cookie" in prev_text:
                result.cookies = table_data
            elif "заголовк" in prev_text:
                result.headers = table_data
            elif "данные формы" in prev_text or "формы" in prev_text:
                result.data = table_data

        return result
