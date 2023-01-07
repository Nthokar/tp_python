import csv
import xml.etree.ElementTree as ET
import requests
url = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req=<date>'


def get_currencies_value(currencies, date):
    response = requests.get(url=url.replace('<date>', date))
    xml_obj = ET.fromstring(response.content)
    currencies_dict = {}
    for child in xml_obj:
        currency = child[1].text
        if currency in currencies:
            if not currencies_dict.keys().__contains__(currency):
                currencies_dict.update({currency: float(child[4].text.replace(',', '.'))/float(child[2].text.replace(',', '.'))})
    return currencies_dict

def date_iter_by_month(left_date, right_date):
    """date format :  dd/mm/yyyy"""
    month_delta = int(right_date.split('/')[2]) * 12 + int(right_date.split('/')[1])\
            - int(left_date.split('/')[2]) * 12 - int(left_date.split('/')[1])
    current_date = int(left_date.split('/')[2]) * 12 + int(left_date.split('/')[1])
    dates = []
    while month_delta > 0:
        current_date_str = '01/' + f'{(current_date % 12 + 1):02}' + '/' + str(current_date // 12)

        dates.append(current_date_str)
        month_delta -= 1
        current_date += 1
    return dates

print(date_iter_by_month('01/10/2020', '01/12/2020'))
def generate_currencies_dataframe(tracking_currencies, left_date, right_date):
    with open('currencies_dataframe', 'w', encoding='utf_8_sig') as w_file:
        writer = csv.writer(w_file)
        writer.writerow(['date'] + tracking_currencies)
        currencies_by_dates = {}
        for date in date_iter_by_month(left_date, right_date):
            currencies_by_date = get_currencies_value(tracking_currencies, date)
            currencies_by_dates.update({date: currencies_by_date})

        for date in currencies_by_dates.keys():
            row = []
            for currency in tracking_currencies:
                row.append(currencies_by_dates[date][currency]) if currency in currencies_by_dates[date] else ' '
            writer.writerow([date] + row)



print(date_iter_by_month('01/10/2016', '01/12/2020'))
generate_currencies_dataframe(['USD', 'EUR', 'BYN', 'AUD'], '01/10/2016', '01/12/2020')