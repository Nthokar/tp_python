import csv
import xml.etree.ElementTree as ET
import requests
url = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req=<date>&d=1'


def get_currencies_value(currencies, date):
    response = requests.get(url=url.replace('<date>', date))
    xml_obj = ET.fromstring(response.content)
    currencies_dict = {}
    for child in xml_obj:
        currency = child[1]
        if currency in currencies:
            if not currencies_dict.keys().__contains__(currency):
                currencies_dict.update({currency: float(child[4])/float(child[2])})
    return currencies_dict

def date_iter_by_month(left_date, right_date):
    """date format :  dd/mm/yyyy"""
    month_delta = int(right_date.split('/')[2]) * 12 + int(right_date.split('/')[1])\
            - int(left_date.split('/')[2]) * 12 - int(left_date.split('/')[1])
    current_date = int(left_date.split('/')[2]) * 12 + int(left_date.split('/')[1])
    dates = []
    while month_delta > 0:
        current_date_str = '01/' + str(current_date % 12 + 1) + '/' + str(current_date // 12)
        dates.append(current_date_str)
        month_delta -= 1
        current_date += 1
    return dates

print(date_iter_by_month('01/10/2020', '01/12/2020'))
def generate_currencies_dataframe():
    with open('currencies_dataframe', 'w', encoding='utf_8_sig') as w_file:
        writer = csv.writer(w_file)
