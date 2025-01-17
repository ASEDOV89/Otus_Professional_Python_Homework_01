import os

import structlog
from structlog.stdlib import LoggerFactory

from src.analyzer.config import load_config, parse_args
from src.analyzer.file_utils import find_latest_log
from src.analyzer.log import get_logger
from src.analyzer.parser import parse_log
from src.analyzer.reporter import render_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": os.path.join(BASE_DIR, "reports"),
    "LOG_DIR": os.path.join(BASE_DIR, "logs"),
}


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def main(config):
    logger = get_logger(config)
    try:
        log_dir = config["LOG_DIR"]
        report_dir = config["REPORT_DIR"]
        report_size = config["REPORT_SIZE"]

        latest_log, report_date = find_latest_log(log_dir)
        if not latest_log:
            print("No logs to process.")
            return

        report_filename = f'report-{report_date.strftime("%Y.%m.%d")}.html'
        report_filepath = os.path.join(report_dir, report_filename)

        if os.path.isfile(report_filepath):
            print(f"Report for {report_date} already exists.")
            return

        log_path = os.path.join(log_dir, latest_log)
        stats = parse_log(log_path)

        report_data = stats[:report_size]

        table_json = [
            {
                "url": url,
                "count": data["count"],
                "count_perc": round(data["count_perc"], 3),
                "time_sum": round(data["time_sum"], 3),
                "time_perc": round(data["time_perc"], 3),
                "time_avg": round(data["time_avg"], 3),
                "time_max": round(data["time_max"], 3),
                "time_med": round(data["time_med"], 3),
            }
            for url, data in report_data
        ]

        render_report(table_json, report_date, report_dir)
        logger.info("Log message", event="my_event", some_key="some_value")

    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
    except ValueError as e:
        logger.error("Value error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)


if __name__ == "__main__":
    args = parse_args()
    config_path = args.config
    user_config = load_config(config_path)
    config = {**default_config, **user_config}

    logger = get_logger(config)

    try:
        main(config)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except FileNotFoundError as e:
        logger.error("Configuration file not found: %s", e)
    except ValueError as e:
        logger.error("Value error: %s", e)
    except Exception as e:
        logger.error("Unexpected error occurred: %s", e, exc_info=True)
        raise
