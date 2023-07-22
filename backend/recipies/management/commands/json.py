import json
import os

from recipies.management.commands._abstract import AbstractCommand


class Command(AbstractCommand):
    """It is not that simple, what it looks like)))"""
    help = "импортировать данные из json файлов и добавить в базу данных"
    FILE_EXTENSION = ".json"

    def import_data(self, path):
        """Импортер данных из файла"""
        self.stdout.write(f'Импорт из файла {path} ...')

        with open(os.path.join(self.DATA_PATH, path),
                  encoding='utf-8') as file:
            reader = json.loads(file.read())
            for row in reader:
                form = self.save_row_to_database(row=row, path=path)
                if form.errors:
                    self.print_error(form=form, row=row, path=path)
