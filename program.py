import csv

import numpy as np
from matplotlib import pyplot as plt
from jinja2 import Environment, FileSystemLoader

import doctest
import unittest

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles.borders import Border, Side

from unittest import TestCase

import pdfkit

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}


def сsv_parser(file_name):
    """Функция читает информацию из файла и создает объекты vacancy,
        которые складывает в два словаря:
            по годам,
            по городам

    :param file_name: Имя csv файла с данными
    :return:
    />>> csv_parser('vacancies_by_year.csv')[0]['2007'][0].salary_currency
    'RUR'
    """

    with open(file_name, encoding='utf_8_sig') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        list_naming = file_reader.__next__()
        vacancies, vacancies_city = {}, {}
        for row in file_reader:
            if len(row) != len(list_naming) or row.__contains__(""):
                continue
            fieds = {}
            for field_index in range(len(row)):
                fieds.update({list_naming[field_index]: row[field_index]})
            year = fieds["published_at"][:4]
            vacancy = Vacancy(name=fieds["name"],
                              salary_from=fieds["salary_from"],
                              salary_to=fieds["salary_to"],
                              salary_currency=fieds["salary_currency"],
                              area_name=fieds["area_name"],
                              published_at=fieds["published_at"])
            if vacancies_city.keys().__contains__(vacancy.area_name):
                vacancies_city[vacancy.area_name].append(vacancy)
            else:
                vacancies_city.update({vacancy.area_name: [vacancy]})
            if vacancies.keys().__contains__(year):
                vacancies[year].append(vacancy)
            else:
                vacancies.update({year: [vacancy]})

        return vacancies, vacancies_city


class VacancyTests(TestCase):
    """Этот класс тестирует коректность инициализации класса Vacancy

    """
    def test_vacancy_type(self):
        self.assertEqual(type(Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300')).__name__,
                         'Vacancy')

    def test_salary_average(self):
        self.assertEqual(Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300').salary_average,
                         15.0)

    def test_salary_currency(self):
        self.assertEqual(Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300').salary_currency,
                         'USD')

class CsvParserTests(TestCase):
    """Этот класс тестирует работу метода csv_parser на заранее определенно верных примерах
    """
    def test_salary_currency(self):
        self.assertEqual(сsv_parser('vacancies_by_year.csv')[0]['2007'][0].salary_currency, 'RUR')

    def test_salary_average(self):
        self.assertEqual(сsv_parser('vacancies_by_year.csv')[0]['2007'][0].salary_average, 40000.0)
class Vacancy:
    """Класс для представления вакансии.
    Attributes:
        name            (str):  Наименование вакансии
        salary_from     (int):  Нижняя граница оклада
        salary_to       (int):  Верхняя граница оклада
        salary_average  (int):  Среднее значение оклада
        salary_currency (str):  Валюта оклада
        area_name       (str):  Название региона вакансии
        published_at    (str):  Дата публикации вакансии
    """

    def __init__(self, name, salary_from, salary_to, salary_currency, area_name, published_at):
        """Инициализирует объект Vacancy, выполняет рассчёт среднего значения оклада

        :param name            (str):  Наименование вакансии
        :param salary_from     (int):  Нижняя граница оклада
        :param salary_to       (int):  Верхняя граница оклада
        :param salary_currency (str):  Валюта оклада
        :param area_name       (str):  Название региона вакансии
        :param published_at    (str):  Дата публикации вакансии

        >>> type(Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300')).__name__
        'Vacancy'
        >>> Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300').salary_average
        15.0
        >>> Vacancy('Программист', 10, 20, 'USD', 'Moscow', '2007-12-03T17:34:36+0300').salary_currency
        'USD'
        """

        self.name = name
        self.salary_from = float(salary_from)
        self.salary_to = float(salary_to)
        self.salary_average = (self.salary_from + self.salary_to) / 2
        self.salary_currency = salary_currency
        self.area_name = area_name
        self.published_at = published_at


class Report:
    """Класс для формирования отчёта

        Attributes:
            font_size (int): размер шрифта в отчёте
    """

    font_size = 12

    def generate_png(self, statics_by_years, statics_by_cities):
        """Функция генерирующая графики по статистике
        Args:
            :param statics_by_years: словарь, содержащий значения типа:
                {год: [средняя зарплата за год, средняя зарплата за год для указанной вакансии,
                 количество вакансий за год, количество указанных вакансий за год]}

            :param statics_by_cities: словарь, содержащий значения типа:
            {город: [средняя зарплата по городу, процент вакансий в городе]}
        """

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(18, 12))
        plt.xticks(fontsize=8)
        years = np.arange(len(statics_by_years.keys()))
        cities = np.arange(len(statics_by_cities))

        colors = ['#FFAC1C', '#FF0000', '#800000', '#FFFF00', '#808000', '#00FF00', '#00FFFF', '#008080', '#0000FF',
                  '#FF00FF', '#800080']

        axes[0][0].bar(years, [x[0] for x in statics_by_years.values()], width=0.4, label="средняя з/п")
        axes[0][0].bar([x + 0.4 for x in years], [x[1] for x in statics_by_years.values()], width=0.4,
                       label="средняя з/п")
        axes[0][0].set_xticks(years, statics_by_years.keys(), rotation=90, ha='right')
        axes[0][0].yaxis.grid(True)
        axes[0][0].set_title("Уровень зарплаты по годам")
        axes[0][0].legend(loc='upper left')

        axes[0][1].bar(years, [x[2] for x in statics_by_years.values()], width=0.4, label="Количество вакансий")
        axes[0][1].bar([x + 0.4 for x in years], [x[3] for x in statics_by_years.values()], width=0.4,
                       label=f"Количество вакансий{name}")
        axes[0][1].set_xticks(years, statics_by_years.keys(), rotation=90, ha='right')
        axes[0][1].yaxis.grid(True)
        axes[0][1].set_title("Количество вакансий по годам")
        axes[0][1].legend(loc='upper left')

        statics_by_cities = dict(sorted(statics_by_cities.items(), key=lambda item: item[1][0], reverse=True))

        axes[1][0].barh(cities, [x[0] for x in statics_by_cities.values()])
        axes[1][0].set_yticks(cities)
        axes[1][0].set_yticklabels(statics_by_cities.keys())
        axes[1][0].invert_yaxis()  # labels read top-to-bottom
        axes[1][0].xaxis.grid(True)
        axes[1][0].set_title('Уровень зарплаты по годам')

        statics_by_cities = dict(sorted(statics_by_cities.items(), key=lambda item: item[1][1], reverse=True))

        axes[1][1].pie(list([x[1] for x in (list(statics_by_cities.values()))[:10]]) + list(
            [sum([x[1] for x in (list(statics_by_cities.values()))[10:]])]),
                       labels=(list(statics_by_cities.keys()))[:10] + ['Другие'], colors=colors)

        fig.savefig('graph.png')
        plt.close(fig)

    def generate_excel(self, statics_by_years, statics_by_cities):
        """Функция генерирующая эксель таблицу по статистике

        Args:
            :param statics_by_years: словарь, содержащий значения типа:
                {год: [средняя зарплата за год, средняя зарплата за год для указанной вакансии,
                 количество вакансий за год, количество указанных вакансий за год]}

            :param statics_by_cities: словарь, содержащий значения типа:
                {город: [средняя зарплата по городу, процент вакансий в городе]}

        """

        wb = Workbook()
        wb.remove(wb['Sheet'])

        statistics_by_year_sheet = wb.create_sheet("Статистика по годам")
        statistics_by_year_sheet.append(["Год", "Средняя зарплата", f"Средняя зарплата - {name}", "Количество вакансий",
                                         f"Количество вакансий - {name}"])
        for key in statics_by_years:
            statistics_by_year_sheet.append([key] + statics_by_years[key])

        cols_dict = {}
        for row in statistics_by_year_sheet.rows:
            for cell in row:
                letter = cell.column_letter
                cell.border = Border(left=Side(style='thin'),
                                     right=Side(style='thin'),
                                     top=Side(style='thin'),
                                     bottom=Side(style='thin'))
                if cell.value:
                    cell.font = Font(name='Calibri', size=self.font_size)
                    len_cell = len(str(cell.value))
                    len_cell_dict = 0
                    if letter in cols_dict:
                        len_cell_dict = cols_dict[letter]

                    if len_cell > len_cell_dict:
                        cols_dict[letter] = len_cell
                        ###!!! ПРОБЛЕМА АВТОМАТИЧЕСКОЙ ПОДГОНКИ !!!###
                        ###!!! расчет новой ширины колонки (здесь надо подгонять) !!!###
                        new_width_col = len_cell * self.font_size ** (self.font_size * 0.009)
                        statistics_by_year_sheet.column_dimensions[cell.column_letter].width = new_width_col

        for cell in statistics_by_year_sheet[1:1]:
            cell.font = Font(name='Calibri', size=self.font_size, bold=True)

        statistics_by_cities_sheet = wb.create_sheet("Статистика по городам")
        statistics_by_cities_sheet.append(['Город', 'Уровень зарплат', ' ', 'Город', 'Доля вакансий'])
        for key in statics_by_cities:
            statistics_by_cities_sheet.append([key, statics_by_cities[key][0], ' ', key, statics_by_cities[key][1]])

        cols_dict = {}
        for row in statistics_by_cities_sheet.rows:
            for cell in row:
                letter = cell.column_letter
                cell.border = Border(left=Side(style='thin'),
                                     right=Side(style='thin'),
                                     top=Side(style='thin'),
                                     bottom=Side(style='thin'))
                if cell.value:
                    cell.font = Font(name='Calibri', size=self.font_size)
                    len_cell = len(str(cell.value))
                    len_cell_dict = 0
                    if letter in cols_dict:
                        len_cell_dict = cols_dict[letter]

                    if len_cell > len_cell_dict:
                        cols_dict[letter] = len_cell
                        ###!!! ПРОБЛЕМА АВТОМАТИЧЕСКОЙ ПОДГОНКИ !!!###
                        ###!!! расчет новой ширины колонки (здесь надо подгонять) !!!###
                        new_width_col = len_cell * self.font_size ** (self.font_size * 0.009)
                        statistics_by_cities_sheet.column_dimensions[cell.column_letter].width = new_width_col

        for cell in statistics_by_cities_sheet['E']:
            cell.number_format = '0.00%'
        for cell in statistics_by_cities_sheet[1:1]:
            cell.font = Font(name='Calibri', size=self.font_size, bold=True)
        wb.save('report.xlsx')

    def generate_report(self, statics_by_years, statics_by_cities):
        """Функция генерирующая пдф файл с отчётом по статистике

        Args:
            :param statics_by_years: словарь, содержащий значения типа:
                {год: [средняя зарплата за год, средняя зарплата за год для указанной вакансии,
                 количество вакансий за год, количество указанных вакансий за год]}

            :param statics_by_cities: словарь, содержащий значения типа:
                {город: [средняя зарплата по городу, процент вакансий в городе]}

        """
        self.generate_png(statics_by_years, statics_by_cities)
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

        pdf_template = template.render({'items': statics_by_years, 'items2': statics_by_cities})
        options = {'enable-local-file-access': None}
        pdfkit.from_string(pdf_template, 'out.pdf', options=options, configuration=config)

isReport = input('Введите данные для печати:') == 'Статистика'

filename, name = input("Введите название файла: "), input("Введите название профессии: ")

"""
при пустом вводе имени файла подставляет стандартное имя файла
"""
if filename == "":
    filename = "vacancies_by_year.csv"

vacancies, vacancies_city = сsv_parser(filename)
vacancies_count = sum(len(vacancies_city[i]) for i in vacancies_city)
city_to_pop = []
for city in vacancies_city:
    if (len(vacancies_city[city]) < int(vacancies_count / 100)):
        city_to_pop.append(city)

for city in city_to_pop:
    vacancies_city.pop(city)

map(lambda k, v: (k, v) if len(vacancies_city[k]) > vacancies_count / 100 else None, vacancies_city)

# region
"""Блок обработки данных, для каждого года находится средний оклад по всем професси и указанной, а также подсчитывается
количество вакансий по всем профессиям и указанной. Для каждого года подсчитывается средняя зп, а также доля вакансий
"""

statistics_by_years = {}
vacancies_count_by_years, vacancies_salary_by_years, \
vacancies_count_by_years_for_name, vacancies_salary_by_years_for_name = {}, {}, {}, {}
for key in vacancies.keys():
    vacancies_count_by_years.update({key: len(vacancies[key])})
    vacancies_salary_by_years.update({key: int(
        sum(x.salary_average * currency_to_rub[x.salary_currency] for x in vacancies[key]) / vacancies_count_by_years[
            key])})
    vacancies_count_by_years_for_name.update({key: len(list(filter(lambda x: (name in x.name), vacancies[key])))})
    if vacancies_count_by_years_for_name[key] == 0:
        vacancies_salary_by_years_for_name.update({key: 0})
    else:
        vacancies_salary_by_years_for_name.update({key: int(sum(
            x.salary_average * currency_to_rub[x.salary_currency] for x in
            list(filter(lambda x: (name in x.name), vacancies[key]))) / vacancies_count_by_years_for_name[key])})
    statistics_by_years.update({key: [vacancies_salary_by_years[key], vacancies_salary_by_years_for_name[key],
                                      vacancies_count_by_years[key], vacancies_count_by_years_for_name[key]]})

statistics_by_cities = {}
vacancies_salary_by_city, vacancies_proportion_by_city = {}, {}
for key in vacancies_city.keys():
    vacancies_salary_by_city.update(
        {key: int(sum(map(lambda x: x.salary_average * currency_to_rub[x.salary_currency], vacancies_city[key])) / len(
            vacancies_city[key]))})
    vacancies_proportion_by_city.update({key: float(len(vacancies_city[key]) / vacancies_count)})
    statistics_by_cities.update(
        {key: [vacancies_salary_by_city[key], round(vacancies_proportion_by_city[key] * 100, 2)]})
# endregion

if isReport:
    Report().generate_report(statistics_by_years, statistics_by_cities)
else:
    Report().generate_excel(statistics_by_years, statistics_by_cities)

# region
"""Блок вывода промежуточных данных в консоль
"""
temp = '\''
print(f"Динамика уровня зарплат по годам: {str(vacancies_salary_by_years).replace(temp, '')}")
print("Динамика количества вакансий по годам: " + str(vacancies_count_by_years).replace(temp, ''))
print(
    "Динамика уровня зарплат по годам для выбранной профессии: " + str(vacancies_salary_by_years_for_name).replace(temp,
                                                                                                                   ''))
print(
    "Динамика количества вакансий по годам для выбранной профессии: " + str(vacancies_count_by_years_for_name).replace(
        temp, ''))
vacancies_salary_by_city = {k: v for k, v in
                            sorted(vacancies_salary_by_city.items(), key=lambda item: item[1], reverse=True)[0:10]}
vacancies_proportion_by_city = {k: round(v, 4) for k, v in
                                sorted(vacancies_proportion_by_city.items(), key=lambda item: item[1], reverse=True)[
                                0:10]}

print("Уровень зарплат по городам (в порядке убывания): " + str(vacancies_salary_by_city))
print(f"Доля вакансий по городам (в порядке убывания): {str(vacancies_proportion_by_city)}")
# endregion
