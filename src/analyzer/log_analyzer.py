import gzip, os, re, json, argparse, sys, logging
from datetime import datetime
from collections import defaultdict
from statistics import median
import structlog
from structlog.stdlib import LoggerFactory


default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

def get_logger(config):
    log_file_path = config.get('LOG_FILE', None)
    logger = structlog.get_logger()
    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        ))
        logging.getLogger().addHandler(file_handler)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        logging.getLogger().handlers[0].setFormatter(structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        ))
    return logger

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
        '--config',
        default='./config.json',
        help='Path to the configuration file (default: ./config.json)'
    )
    return parser.parse_args()

def find_latest_log(log_dir):
    log_file_pattern = re.compile(r'nginx-access-ui\.log-(\d{8})\.gz$')
    latest_date = None
    latest_file = None

    for file in os.listdir(log_dir):
        match = log_file_pattern.search(file)
        if match:
            file_date = datetime.strptime(match.group(1), '%Y%m%d').date()
            if not latest_date or file_date > latest_date:
                latest_date = file_date
                latest_file = file

    return latest_file, latest_date

def open_log_file(log_path):
    if log_path.endswith('.gz'):
        return gzip.open(log_path, 'rt')
    else:
        return open(log_path, 'r')

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

def parse_line(line):
    log_pattern = re.compile(
        r'(?P<remote_addr>\S+) '
        r'(?P<remote_user>\S+) '
        r'(?P<http_x_real_ip>\S+) '
        r'\[(?P<time_local>.+)\] '
        r'"(?P<request>.+?)" '
        r'(?P<status>\S+) '
        r'(?P<body_bytes_sent>\S+) '
        r'"(?P<http_referer>.+?)" '
        r'"(?P<http_user_agent>.+?)" '
        r'(?P<http_x_forwarded_for>\S+) '
        r'(?P<http_X_REQUEST_ID>\S+) '
        r'(?P<http_X_RB_USER>\S+) '
        r'(?P<request_time>\S+)'
    )
    match = log_pattern.match(line)
    if match:
        request = match.group('request')
        request_time = float(match.group('request_time'))
        url = request.split()[1]
        return url, request_time
    return None

def parse_log(log_path):
    url_stats = defaultdict(lambda: defaultdict(float))
    total_count = 0
    total_time = 0

    with open_log_file(log_path) as file:
        for line in file:
            parsed_line = parse_line(line)
            if parsed_line:
                url, request_time = parsed_line
                url_stats[url]['count'] += 1
                url_stats[url]['time_sum'] += request_time
                url_stats[url]['time_max'] = max(url_stats[url]['time_max'], request_time)
                url_stats[url]['times'].append(request_time)
                total_count += 1
                total_time += request_time

    for url, stats in url_stats.items():
        stats['count_perc'] = (stats['count'] / total_count) * 100
        stats['time_perc'] = (stats['time_sum'] / total_time) * 100
        stats['time_avg'] = stats['time_sum'] / stats['count']
        stats['time_med'] = median(stats['times'])
        del stats['times']

    return sorted(url_stats.items(), key=lambda item: item[1]['time_sum'], reverse=True)

def render_report(table_json, report_date, report_dir):
    with open('templates/report.html', 'r') as report_template:
        report_html = report_template.read()

    report_html = report_html.replace('$table_json', json.dumps(table_json))

    report_filename = f'report-{report_date.strftime("%Y.%m.%d")}.html'
    report_filepath = os.path.join(report_dir, report_filename)

    with open(report_filepath, 'w') as report_file:
        report_file.write(report_html)


def main(config):
    logger = get_logger(config)
    try:
        log_dir = config['LOG_DIR']
        report_dir = config['REPORT_DIR']
        report_size = config['REPORT_SIZE']

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
                'url': url,
                'count': data['count'],
                'count_perc': round(data['count_perc'], 3),
                'time_sum': round(data['time_sum'], 3),
                'time_perc': round(data['time_perc'], 3),
                'time_avg': round(data['time_avg'], 3),
                'time_max': round(data['time_max'], 3),
                'time_med': round(data['time_med'], 3),
            } for url, data in report_data
        ]

        render_report(table_json, report_date, report_dir)
        logger.info("Log message", event="my_event", some_key="some_value")
    except Exception as e:
        logger.error("unexpected_error", exc_info=True)

if __name__ == "__main__":
    args = parse_args()
    config_path = args.config
    user_config = load_config(config_path)
    config = {**default_config, **user_config}

    try:
        main(config)
    except KeyboardInterrupt:
        get_logger(config).info("Script interrupted by user")
    except Exception as e:
        get_logger(config).error("unexpected_error", exc_info=True)
        raise e
