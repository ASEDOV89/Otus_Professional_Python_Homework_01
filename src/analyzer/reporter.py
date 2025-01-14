import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render_report(table_json, report_date, report_dir):
    template_path = os.path.join(
        BASE_DIR, "src", "analyzer", "templates", "report.html"
    )
    with open(template_path, "r") as report_template:
        report_html = report_template.read()

    report_html = report_html.replace("$table_json", json.dumps(table_json))

    report_filename = f'report-{report_date.strftime("%Y.%m.%d")}.html'
    report_filepath = os.path.join(report_dir, report_filename)

    with open(report_filepath, "w") as report_file:
        report_file.write(report_html)
