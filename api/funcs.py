import re
from datetime import datetime


def format_date(text):
    patterns = [
        r'(\d{2})[ .-](\d{2})[ .-](\d{4})',
        r'(\d{4})[ .-](\d{2})[ .-](\d{2})',
        r'(\d{1,2}) (\d{1,2}) (\d{4})',
        r'(\d{1,2})[ .-](\d{1,2})[ .-](\d{2})',
        r'(\d{1,2}) ([а-яА-Я]+) (\d{4})',
    ]
    months = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                day, month, year = groups
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                if month.isalpha():
                    month = months.get(month.lower(), '01')
                try:
                    date = datetime(int(year), int(month), int(day)).strftime('%Y-%m-%d')
                    return date
                except ValueError:
                    continue
    return ''


def format_tables_info(full_data):
    full_new_data = []
    for data in full_data:
        new_dates = []
        for date in data['dates']:
            if data['dates'].count(date) > 1:
                data['dates'].remove(date)
        for date in data['dates']:
            new_dates.append(format_date(date))
        data['dates'] = new_dates
        min_len = min(len(data['dates']), len(data['records']), len(data['stamps']))
        for i in range(min_len):
            full_new_data.append({
                f'entry_date': data['dates'][i],
                f'entry_info': data['records'][i],
                f'entry_stamp': data['stamps'][i]
            })
    return full_new_data
