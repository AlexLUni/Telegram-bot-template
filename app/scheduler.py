from datetime import datetime

import pytz

from app.database.uow import UnitOfWork


async def check_outdated() -> None:
    """Remove all temporary entries which have expired."""
    moscow_tz = pytz.timezone('Europe/Moscow')
    today = datetime.now(moscow_tz)
    async with UnitOfWork(auto_commit=True) as uow:
        all_temp = await uow.temp.find(filters={})
        for temp_message in all_temp:
            day = int(temp_message.date.split('.')[0])
            month = int(temp_message.date.split('.')[1])
            year = int(f"{temp_message.date.split('.')[2]}")
            date = datetime(year, month, day, 22, 30, tzinfo=moscow_tz)

            if today > date:
                await uow.temp.delete(temp_message)
