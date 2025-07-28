import asyncio
import csv
import random

import requests
from bs4 import BeautifulSoup

from settings import settings


def save_to_csv(headers: list, data: list, path: str = "result.csv") -> None:
    """
    Сохранить таблицу в csv.

    Args:
        headers: Заголовок.
        data: Данные таблицы.
        path: Путь сохранения.
    """
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


def print_data(headers: list, data: list) -> None:
    """
    Вывести таблицу.

    Args:
        headers: Заголовок.
        data: Данные таблицы.
    """
    print(" | ".join(headers))
    for row in data:
        print(" | ".join(row))


async def delay(base_delay: float = 1.0, delay_multiplier: float = 1.0) -> None:
    """
    Задержка между запросами.

    Args:
        base_delay: Базовая задержка между запросами.
        delay_multiplier: Множитель задержки.
    """
    await asyncio.sleep(base_delay + random.random() * delay_multiplier)


async def parse_table(
    base_url: str,
    login: str,
    password: str,
    db_name: str,
    table_name: str,
    base_delay: float = 1.0,
    delay_multiplier: float = 1.0,
) -> tuple[list[str], list[list]]:
    """
    Аутентификация и получения таблицы.

    Args:
        login: Логин.
        password: Пароль.
        base_url: Базовый URL.
        db_name: Название БД.
        table_name: Название таблицы
        base_delay: Базовая задержка между запросами.
        delay_multiplier: Множитель задержки.

    Returns:
        Заголовок и данные таблицы.
    """
    token, session = await authentication(
        base_url, login, password, base_delay, delay_multiplier
    )

    await delay(base_delay, delay_multiplier)

    return await get_table(
        session, base_url, db_name, table_name, token, base_delay, delay_multiplier
    )


async def authentication(
    base_url: str,
    login: str,
    password: str,
    base_delay: float = 1.0,
    delay_multiplier: float = 1.0,
) -> tuple[str, requests.Session]:
    """
    Аутентификация.

    Args:
        login: Логин.
        password: Пароль.
        base_url: Базовый URL.
        base_delay: Базовая задержка между запросами.
        delay_multiplier: Множитель задержки.

    Returns:
        Токен и HTTP сессия.
    """
    session = requests.Session()
    login_page = session.get(base_url)

    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.find("input", {"name": "token"})["value"]

    login_data = {
        "pma_username": login,
        "pma_password": password,
        "server": "1",
        "token": token,
    }

    await delay(base_delay, delay_multiplier)

    session.post(f"{base_url}index.php", data=login_data)

    return token, session


async def get_table(
    session,
    base_url: str,
    db_name: str,
    table_name: str,
    token: str,
    base_delay: float = 1.0,
    delay_multiplier: float = 1.0,
) -> tuple[list[str], list[list]]:
    """
    Получает таблицу.

    Args:
        session: HTTP сессия.
        base_url: Базовый URL.
        db_name: Название БД.
        table_name: Название таблицы
        token: Токен.
        base_delay: Базовая задержка между запросами.
        delay_multiplier: Множитель задержки.

    Returns:
        Заголовок и данные таблицы.
    """
    session.get(
        f"{base_url}index.php?route=/database/structure&db={db_name}&token={token}"
    )

    await delay(base_delay, delay_multiplier)

    table_response = session.get(
        f"{base_url}index.php?route=/sql&db={db_name}&table={table_name}&token={token}"
    )
    table_bs = BeautifulSoup(table_response.text, "html.parser").find(
        "table", class_=["table", "data", "table_results"]
    )

    headers = [
        cell.text.strip()
        for cell in table_bs.find("tr").find_all(["th"])
        if cell.text.strip()
    ]

    rows = table_bs.find_all("tr")[1:]
    data = []
    for row in rows:
        cells = row.find_all(["td"])[4:]
        data.append([cell.text.strip() for cell in cells])

    return headers, data


async def main() -> None:
    """Считывает таблицу, сохраняет ее в csv файл, выводит в консоль."""
    headers, data = await parse_table(
        settings.BASE_URL,
        settings.LOGIN,
        settings.PASSWORD,
        settings.DB_NAME,
        settings.TABLE_NAME,
        settings.BASE_DELAY,
        settings.DELAY_MULTIPLIER,
    )

    save_to_csv(headers, data)
    print_data(headers, data)


if __name__ == "__main__":
    asyncio.run(main())
