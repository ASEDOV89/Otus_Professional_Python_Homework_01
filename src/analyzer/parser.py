import re
from collections import defaultdict
from statistics import median

from src.analyzer.file_utils import open_log_file


def parse_line(line):
    log_pattern = re.compile(
        r"(?P<remote_addr>S+) "
        r"(?P<remote_user>S+) "
        r"(?P<http_x_real_ip>S+) "
        r"[(?P<time_local>.+)] "
        r'"(?P<request>.+?)" '
        r"(?P<status>S+) "
        r"(?P<body_bytes_sent>S+) "
        r'"(?P<http_referer>.+?)" '
        r'"(?P<http_user_agent>.+?)" '
        r"(?P<http_x_forwarded_for>S+) "
        r"(?P<http_X_REQUEST_ID>S+) "
        r"(?P<http_X_RB_USER>S+) "
        r"(?P<request_time>S+)"
    )
    match = log_pattern.match(line)
    if match:
        request = match.group("request")
        request_time = float(match.group("request_time"))
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
                url_stats[url]["count"] += 1
                url_stats[url]["time_sum"] += request_time
                url_stats[url]["time_max"] = max(
                    url_stats[url]["time_max"], request_time
                )
                url_stats[url]["times"].append(request_time)
                total_count += 1
                total_time += request_time

    for url, stats in url_stats.items():
        stats["count_perc"] = (stats["count"] / total_count) * 100
        stats["time_perc"] = (stats["time_sum"] / total_time) * 100
        stats["time_avg"] = stats["time_sum"] / stats["count"]
        stats["time_med"] = median(stats["times"])
        del stats["times"]

    return sorted(
        url_stats.items(),
        key=lambda item: item[1]["time_sum"],
        reverse=True,
    )
