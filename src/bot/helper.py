import datetime
import json
import re
from enum import Enum
from uuid import UUID

import requests
from typing import List, Dict, Any, Tuple

from src.errors import (
    InternalServerError,
    UnknownError,
    UnprocessableEntityError,
    NotFoundError,
    AlreadyExistsError
)
from src.settings import settings


class RequestType(str, Enum):
    get = 'GET'
    post = 'POST'
    put = 'PUT'
    patch = 'PATCH'
    delete = 'DELETE'


class RequestsHelper:
    @classmethod
    async def create_request(
            self,
            url: str,
            request_type: RequestType,
            data: Dict[str, Any] | None = None,
            params: Dict[str, Any] | None = None,
    ):
        response = None
        data_json = json.dumps(data) if data else None
        if request_type == RequestType.get:
            response = requests.get(url, params=params)
        elif request_type == RequestType.post:
            response = requests.post(url, data=data_json, params=params)
        elif request_type == RequestType.put:
            response = requests.put(url, data=data_json, params=params)
        elif request_type == RequestType.patch:
            response = requests.patch(url, data=data_json, params=params)
        elif request_type == RequestType.delete:
            response = requests.delete(url, data=data_json, params=params)
        await self._process_errors(response)
        return response

    @classmethod
    async def _process_errors(cls, response):
        if response.status_code == 200:
            return True
        if response.status_code == 500:
            raise InternalServerError
        if response.status_code == 404:
            raise NotFoundError
        if response.status_code == 409:
            raise AlreadyExistsError
        if response.status_code == 422:
            raise UnprocessableEntityError
        raise UnknownError


class TelegramHelper:
    @staticmethod
    def _escape_markdown_v2(text: str | None = None) -> str:
        if not text:
            return text
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    @staticmethod
    def _create_spoiler(text: str) -> str:
        return '||' + text + '||'


class ContactHelper(RequestsHelper, TelegramHelper):
    @classmethod
    async def create_contact(cls, name: str):
        await cls.create_request(
            settings.server.api_url + '/contacts/create/',
            RequestType.post,
            {'name': name}
        )

    @classmethod
    async def update_contact(cls, name: str, field_to_update: str, new_value: Any) -> Dict[str, str] | None:
        field_to_update = field_to_update.lower()

        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/get/',
            RequestType.get
        )

        contact = response.json()

        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/update/',
            RequestType.put,
            {field_to_update: new_value}
        )

        return {
            'field': field_to_update.title(),
            'old_value': contact[field_to_update],
            'new_value': new_value
        }

    @classmethod
    async def find_contacts_by_name(cls, name: str) -> List[str] | None:
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/get_similar/',
            RequestType.get
        )

        contacts = response.json()
        contact_names = [contact['name'] for contact in contacts]
        return contact_names

    @classmethod
    async def convert_contact_data_to_string(cls, contact: Dict[str, str]) -> str:
        result = [
            f"*{cls._escape_markdown_v2(contact['name'])}*",
            ""
        ]
        if contact['telegram']:
            telegram = contact['telegram']
            telegram = cls._escape_markdown_v2(telegram)
            result.append(f"✈️ Telegram: {telegram}")
        if contact['phone']:
            phone = contact['phone']
            phone = cls._escape_markdown_v2(phone)
            result.append(f"📞 Phone: {phone}")
        if contact['birthday']:
            birthday = contact['birthday']
            birthday = cls._escape_markdown_v2(birthday)
            result.append(f"🎉 Birthday: {birthday}")
        return "\n".join(result)

    @classmethod
    async def get_contact_by_name(cls, name: str):
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/get/',
            RequestType.get
        )
        contact = response.json()
        return contact

    @classmethod
    async def get_contact_data_by_name(cls, name: str) -> Dict[str, str] | None:
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/get/',
            RequestType.get,
        )
        contact = response.json()
        return contact

    @classmethod
    async def delete_contact(cls, name: str):
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/delete/',
            RequestType.delete,
        )

    @classmethod
    async def get_last_contacts(cls):
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/get_lasts/',
            RequestType.get,
        )
        return [contact['name'] for contact in response.json()]

    @classmethod
    async def get_all_contacts(cls) -> str:
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/get/',
            RequestType.get,
        )
        contacts = response.json()
        res = []
        for contact in contacts:
            name = cls._escape_markdown_v2(contact['name'])
            telegram = cls._escape_markdown_v2(contact['telegram'])
            row = f'— {name} \({telegram}\)' if telegram else f'— {name}'
            res.append(row)
        text = "\n".join(sorted(res))
        return text


class LogHelper(RequestsHelper, TelegramHelper):

    @staticmethod
    def text_is_empty(text: str) -> bool:
        if not text or text == "" or text == '||||':
            return True
        return False

    @classmethod
    async def convert_logs_to_str(cls, logs) -> str:
        result_list = []
        for data in logs:
            date = str(data['date'])
            date = cls._escape_markdown_v2(date)
            result_list.append(f"\n*{date}:*")
            for log in data['logs']:
                log_text = cls._escape_markdown_v2(log['log'])
                result_list.append(f"— {log['number']}: {log_text}")

        text = '\n'.join(result_list)
        p1, p2 = 0, len(result_list) - 1
        while p1 < p2:
            m = (p1 + p2) // 2
            text = '\n'.join(result_list[m:])
            if len(text) > 4000:
                p1 = m + 1
            else:
                p2 = m

        if len(text) > 0 and text[0] == '\n':
            text = text[1:]
        return cls._create_spoiler(text)

    @classmethod
    async def get_all_logs(cls, name: str) -> Tuple[str, Dict[int, UUID]]:
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/logs/get_all/list/',
            RequestType.get
        )
        logs = response.json()['data']
        numbers_to_log_id = response.json()['numbers_to_log_id']
        return await cls.convert_logs_to_str(logs), numbers_to_log_id

    @classmethod
    async def add_log(cls, log_str: str, name: str, date: datetime.date | None = None):
        print(f'{log_str = }, {name = }, {date = }')
        if date is None:
            await cls.create_request(
                f'{settings.server.api_url}/contacts/{name}/logs/create/',
                RequestType.post,
                {
                    'name': name,
                    'log': log_str
                }
            )
        else:
            await cls.create_request(
                f'{settings.server.api_url}/contacts/{name}/logs/create/{date}',
                RequestType.post,
                {
                    'name': name,
                    'log': log_str
                }
            )

    @classmethod
    async def add_empty_log(cls, name: str):
        response = await cls.create_request(
            f'{settings.server.api_url}/contacts/{name}/logs/create/empty/',
            RequestType.post,
            {'name': name}
        )

    @classmethod
    async def get_last_logs(cls):
        response = await cls.create_request(
            f'{settings.server.api_url}/logs/last_logs',
            RequestType.get
        )
        logs_dict = response.json()
        result = []
        for name, logs_data in logs_dict.items():
            name = cls._escape_markdown_v2(name)
            result.append(f'*\n{name}:*')
            for date, logs in logs_data.items():
                for log in logs:
                    if log and log != "":
                        log = cls._escape_markdown_v2(log)
                        result.append(f'— {log}')
        text = "\n".join(result)
        return cls._create_spoiler(text)

    @classmethod
    async def edit_log_text(cls, log_id: UUID, new_text: str):
        response = await cls.create_request(
            f'{settings.server.api_url}/logs/{log_id}/update/',
            RequestType.put,
            {'log': new_text}
        )

    @classmethod
    async def edit_log_date(cls, log_id: int, new_date: str):
        response = await cls.create_request(
            f'{settings.server.api_url}/logs/edit/{log_id}/by_date',
            RequestType.put,
            params={'date': new_date}
        )

    @classmethod
    async def delete_log(cls, log_id: int):
        response = await cls.create_request(
            f'{settings.server.api_url}/logs/{log_id}/delete/',
            RequestType.delete
        )

    @classmethod
    def create_str_for_logs(self, all_logs: str, name: str) -> str:
        return f'📋 Logs for *{Helper._escape_markdown_v2(name)}*:\n\n{all_logs}'

    @classmethod
    async def get_log_by_id(cls, log_id: int):
        response = await cls.create_request(
            f'{settings.server.api_url}/logs/{log_id}/get/',
            RequestType.get
        )
        return response.json()


class StatsHelper(RequestsHelper, TelegramHelper):

    @classmethod
    async def _get_telegram_by_name(cls, name: str) -> str:
        contact = await ContactHelper.get_contact_by_name(name)
        return contact['telegram']

    @classmethod
    async def get_days_count_since_last_interaction(cls):
        def add_title(day_count: int, result: List[str]) -> None:
            class Types(str, Enum):
                recent = '*Recent:*'
                average = '*Average:*'
                long = '*Long*:'

            result_set = set(result)
            if day_count < 7 and Types.recent not in result_set:
                result.append("")
                result.append(Types.recent)
            elif 7 <= day_count < 30 and Types.average not in result_set:
                result.append("")
                result.append(Types.average)
            elif 30 <= day_count and Types.long not in result_set:
                result.append("")
                result.append(Types.long)

        response = await cls.create_request(
            f'{settings.server.api_url}/stats/days_count_since_last_interaction/',
            RequestType.get
        )
        contacts_with_days: List[Tuple[str, int]] = []
        for data in response.json():
            name = data['name']
            day_count = data['day_count']
            contacts_with_days.append((name, day_count))
        contacts_with_days.sort(key=lambda x: x[1], reverse=True)

        result: List[str] = []
        for name, day_count in contacts_with_days:
            add_title(day_count, result)
            telegram = await cls._get_telegram_by_name(name)
            result.append(
                f"— {day_count} days: {cls._escape_markdown_v2(name)} \({cls._escape_markdown_v2(telegram)}\)")

        return "\n".join(result)


class Helper(ContactHelper, LogHelper, StatsHelper):
    pass
