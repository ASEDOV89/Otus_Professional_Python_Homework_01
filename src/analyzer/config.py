import argparse
import json
import os
import sys


def load_config(path):
    if not os.path.exists(path):
        print(f"Config file {path} does not exist.")
        sys.exit(1)
    with open(path) as config_file:
        try:
            config = json.load(config_file)
        except ValueError as e:
            print(f"Invalid config format: {e}")
            sys.exit(1)
    return config


def parse_args():
    parser = argparse.ArgumentParser(description="Log Analyzer")
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Папка с файлом конфигурации (default: config/config.json)",
    )
    return parser.parse_args()
