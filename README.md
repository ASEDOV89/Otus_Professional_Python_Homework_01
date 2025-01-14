**Команды**

Запуск приложения:  
poetry run python src/main.py  

Докер:  
docker build -t homework_01 .  
docker-compose up -d  

Тесты:  
	poetry run pytest tests/  
	poetry run flake8 src/ tests/  


**Структура проекта**

├── Dockerfile  
├── Makefile  
├── README.md  
├── config  
│   └── config.json  
├── description.pdf  
├── docker-compose.yaml  
├── lecture.ipynb  
├── logs  
│   └── nginx-access-ui.log-20170630.gz  
├── poetry.lock  
├── pyproject.toml  
├── reports  
│   └── report-2017.06.30.html  
├── src  
│   ├── __init__.py  
│   ├── analyzer  
│   │   ├── __init__.py  
│   │   ├── config.py  
│   │   ├── docs  
│   │   │   └── homework.pdf  
│   │   ├── file_utils.py  
│   │   ├── log.py  
│   │   ├── log_analyzer.py  
│   │   ├── parser.py  
│   │   └── reporter.py  
│   ├── app  
│   │   ├── __init__.py  
│   │   └── module.py  
│   ├── lecture.ipynb  
│   ├── main.py  
│   └── templates  
│       ├── jquery.tablesorter.min.js  
│       └── report.html  
├── tests  
│   ├── __init__.py  
│   └── test_log_analyzer.py  
└── type_annotations-534944-cafdd4.ipynb  