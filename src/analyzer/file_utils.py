import gzip
import os
import re
from datetime import datetime


def find_latest_log(log_dir):
    log_file_pattern = re.compile(r"nginx-access-ui.log-(\d{8}).gz$")
    latest_date = None
    latest_file = None

    print(f"Содержимое директории {log_dir}: {os.listdir(log_dir)}")

    for file in os.listdir(log_dir):
        match = log_file_pattern.search(file)
        if match:
            file_date = datetime.strptime(match.group(1), "%Y%m%d").date()
            print(f"Найден файл: {file}, дата: {file_date}")

            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = file
                print(f"Обновлено: {latest_file} с датой {latest_date}")

    if latest_file is None:
        print("Не найдено ни одного подходящего файла.")
    return latest_file, latest_date


def open_log_file(log_path):
    if log_path.suffix == ".gz":
        return gzip.open(log_path, "rt")
    else:
        return open(log_path, "r")
