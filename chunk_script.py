import csv


def generate_chunks(file_name):
    with open(file_name, encoding='utf_8_sig') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        list_naming = file_reader.__next__()
        list_of_years = {}
        date_index = 0
        if list_naming.__contains__('published_at'):
            for i in range(len(list_naming)):
                if list_naming[i] == 'published_at':
                    date_index = i
        else:
            return
        for row in file_reader:
            date = row[date_index][:4]
            if list_of_years.__contains__(date):
                list_of_years[date].append(row)
            else:
                list_of_years.update({date: [row]})
        for date in list_of_years.keys():
            with open(file_name.split('.')[0] + '_' + date + '.csv', 'w', encoding='utf_8_sig') as w_file:
                writer = csv.writer(w_file)
                writer.writerow(list_naming)
                for row in list_of_years[date]:
                    writer.writerow(row)


generate_chunks('data\\vacancies_dif_currencies.csv')