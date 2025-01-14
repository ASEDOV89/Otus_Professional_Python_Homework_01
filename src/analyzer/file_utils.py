import re
import os
import gzip
import datetime


def find_latest_log(log_dir):
    log_file_pattern = re.compile(r"nginx-access-ui\.log-(\d{8})\.gz$")
    latest_date = None
    latest_file = None

    for file in os.listdir(log_dir):
        match = log_file_pattern.search(file)
        if match:
            file_date = datetime.strptime(match.group(1), "%Y%m%d").date()
            if not latest_date or file_date > latest_date:
                latest_date = file_date
                latest_file = file

    return latest_file, latest_date


def open_log_file(log_path):
    if log_path.endswith(".gz"):
        return gzip.open(log_path, "rt")
    else:
        return open(log_path, "r")
