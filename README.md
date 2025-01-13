Move along. Nothing to see here
├── Dockerfile
├── README.md
├── config
│   └── config.json
├── docker-compose.yaml
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── analyzer
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── log.py
│   │   └── log_analyzer.py
│   ├── main.py
│   └── templates
│       ├── jquery.tablesorter.min.js
│       └── report.html
├── tests
│   ├── __init__.py
│   └── test_log_analyzer.py
├── logs  # Папка для хранения логов (должна быть исключена из репозитория)
└── reports  # Папка для хранения отчетов (должна быть исключена из репозитория)