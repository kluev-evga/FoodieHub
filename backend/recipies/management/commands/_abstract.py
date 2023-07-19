import os
import sys
from glob import glob

from recipies.management.commands._forms import (
    FavoriteForm,
    IngredientForm,
    RecipeForm,
    ShoppingCartForm,
    TagForm
)
from django.core.management import BaseCommand, CommandError


class AbstractCommand(BaseCommand):
    requires_migrations_checks = True
    requires_system_checks = ()
    suppressed_base_arguments = (
        "--traceback",
        "--no-color",
        "--force-color",
        "--verbosity",
        "--settings",
        "--version",
        "--pythonpath")
    FORMS = {
        "recipe": RecipeForm,
        "shoppingcart": ShoppingCartForm,
        "ingredient": IngredientForm,
        "favourite": FavoriteForm,
        "tag": TagForm
    }
    FILE_EXTENSION = None
    DEFAULT_PATH = "../data/"
    DATA_PATH = None
    INVALID_FILES = []

    def import_data(self, path):
        raise NotImplementedError()

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help=f"импортировать все {self.FILE_EXTENSION} файлы")
        parser.add_argument(
            '--path',
            help=(f"путь до директории с {self.FILE_EXTENSION} "
                  "файлами относительно manage.py"))

    def handle(self, *args, **kwargs):
        """Конкатенировать расширения,
           обработать полученные флаги,
           получить валидный список файлов,
           выполнить импорт по каждому"""
        self.FORMS = {key + self.FILE_EXTENSION: value
                      for key, value in self.FORMS.items()}

        if kwargs.get("path"):
            self.DATA_PATH = kwargs.get("path")
        else:
            self.DATA_PATH = self.DEFAULT_PATH

        if kwargs.get("all"):
            files_list = self.get_files_list()
        else:
            files_list = self.prompt_files_list()

        for file in files_list:
            self.import_data(file)

    def save_row_to_database(self, row, path):
        """Проверить валидность строки данных и записать в БД"""
        form = self.FORMS[path](data=row)
        if form.is_valid():
            form.save()
        return form

    def print_error(self, form, row, path):
        self.stderr.write(
            f"Ошибка импорта из {path}: {row}:\n{form.errors.as_data()}\n"
        )

    def validate_files_list(self, files_list):
        """Проверить на пустой список и правильные имена файлов"""
        if not files_list:
            message = (f"{self.DATA_PATH}: файлы"
                       f" {self.FILE_EXTENSION} не найдены"
                       ", проверьте путь до файлов.")
            raise CommandError(message)

        valid_file_names = self.get_valid_filenames()
        validated_file_names = []
        for file in files_list:
            if file not in valid_file_names:
                self.INVALID_FILES.append(file)
            else:
                validated_file_names.append(file)
        if self.INVALID_FILES:
            message = (f"\033[0;32m{'_' * 35}\nОжидаемые файлы:"
                       f"\n{self.format_names(self.get_valid_filenames())}"
                       "\n\033[0;31mНе будут обработаны:\n"
                       f"{self.format_names(self.INVALID_FILES)}"
                       f"\033[0;32m{'_' * 35}\033[0m\n")
            self.stdout.write(message)
        return validated_file_names

    def get_files_list(self):
        """Вернуть список файлов для директории - DATA_PATH"""
        path = self.DATA_PATH + "*" + self.FILE_EXTENSION
        files_list = [os.path.basename(file) for file in glob(path)]
        return self.validate_files_list(files_list)

    def prompt_files_list(self):
        """Запросить имена файлов, если не передан флаг --all"""
        files_list = self.get_files_list()

        input_message = ("\n\033[0;32mНайдены файлы:"
                         f"\n{self.format_names(files_list)}"
                         "\nEnter - выбрать все"
                         "\n1,2,3 - выбрать через запятую"
                         "\nQ     - выйти\033[0m\n")
        error_message = "\033[0;31mНекорректный ввод, попробуйте еще раз:\033[0m"

        selection = input(input_message)
        valid_values = tuple(range(1, len(files_list) + 1))
        while True:
            selection.lower() == 'q' and sys.exit()
            if selection == "":
                selection = valid_values
                break
            else:
                try:
                    selection = [int(val)
                                 for val in selection.split(",") if val != ""]
                    for value in selection:
                        if value not in valid_values:
                            raise ValueError()
                    break
                except ValueError:
                    self.stdout.write(error_message)
            selection = input()

        return [files_list[num - 1] for num in selection]

    @staticmethod
    def format_names(names_list):
        """Отформатировать список файлов построчно с отступом"""
        string = ""
        for num, file in enumerate(names_list, start=1):
            string += f"   {num}  {file}\n"
        return string

    def get_valid_filenames(self):
        return self.FORMS.keys()
