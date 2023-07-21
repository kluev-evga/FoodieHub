import csv
import os

from recipies.management.commands._abstract import AbstractCommand


class Command(AbstractCommand):
    """It is not that simple, what it looks like)))"""
    help = "импортировать данные из csv файлов и добавить в базу данных"
    FILE_EXTENSION = ".csv"

    def import_data(self, path):
        """Извлечь данные из CSV, вызвать валидацию и распечатать ошибки"""
        self.stdout.write(f'{"_" * 35}\nИмпорт из файла {path}\n{"_" * 35}\n')

        with open(os.path.join(self.DATA_PATH, path),
                  mode='r',
                  encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                form = self.save_row_to_database(row=row, path=path)
                if form.errors:
                    self.print_error(form=form, row=row, path=path)
