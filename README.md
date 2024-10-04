# Анализатор лог-файлов прокси-сервера NGINX

Примитивный анализатор, поддерживающий парсинг и подсчет ключевых метрик времени запроса.

## Описание

Анализатор поддерживает лог-файлы прокси-сервера NGINX следующего формата:
```
log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
                    '$request_time'
```

Производит парсинг лог-файла и расчет следующих метрик:
* count - сколько раз встречается URL, абсолютное значение;
* count_perc - сколько раз встречается URL, в процентнах относительно общего числа запросов;
* time_sum - суммарный \$request_time для данного URL'а, абсолютное значение;
* time_perc - суммарный \$request_time для данного URL'а, в процентах относительно общего $request_time всех запросов;
* time_avg - средний \$request_time для данного URL'а;
* time_max - максимальный \$request_time для данного URL'а;
* time_med - медиана \$request_time для данного URL'а.

Имеет конфигурацию по умолчанию, поддерживается кастомную конфигурацию (см. раздел [Запуск с кастомной конфигурацией](#запуск-с-кастомной-конфигурацией))

## Эксплуатация

### Системные требования

* `Python` версии `3.12` или выше
* `Poetry` версии `1.8.3` или выше

### Установка

1. Склонируйте проект:
```
git clone ...
```
2. Установите зависимости:
```
poetry install
```

### Запуск

#### Запуск с конфигурацией по умолчанию
1. В корневом каталоге создайте директории `log` и `reports`
```
.
├── log/
└── reports/
```
2. Расположите шаблон отчета в корневом каталоге
```
.
├── log/
├── reports/
└── report.html
```
3. Поместите лог-файлы сервиса в директорию `log`
```
.
├── log/
│   ├── nginx-access-ui.log-20170630.gz
│   ├── nginx-access-ui.log-20170708.bz2
│   ├── nginx-access-ui.log-20170730
│   └── ...
├── reports/
└── report.html
```
4. Поместите в директорию с отчетами библиотеку [jquery.tablesorter.min.js](https://mottie.github.io/tablesorter/dist/js/jquery.tablesorter.min.js)
5. Войдите в виртуальное окружение
```
poetry shell
```
6. Запустите анализатор
```
python main.py
```
Результатом работы представленного примера будет созданный файл отчета `report-20170730.html` в директории `reports`
```
.
├── log/
│   ├── nginx-access-ui.log-20170630.gz
│   ├── nginx-access-ui.log-20170708.bz2
│   ├── nginx-access-ui.log-20170730
│   └── ...
├── reports/
│   └── report-20170730.html
└── report.html
```

#### Запуск с кастомной конфигурацией
1. Создайте файл config.json
2. Заполните, ориентируясь на пример:
```
{
    "REPORT_SIZE": 1000, # данный параметр влияет на количество записей с максимальным `time_sum`, попадающих в отчет
    "REPORT_DIR": "./reports", # путь к директории с отчетами
    "LOG_DIR": "./log", # путь к директории с анализируемыми лог-файлами
    "LOG_FILE": "log.log" # путь к файлу, в который запишется лог работы анализатора, по умолчанию лог записывается в консоль
}
```
3. Создайте директории, которые указаны в параметрах конфигурации `LOG_DIR` и `REPORT_DIR`
```
.
├── log/
└── reports/
```
2. Расположите шаблон отчета в каталоге запуска программы
```
.
├── log/
├── reports/
└── report.html
```
3. Поместите лог-файлы сервиса в директорию, указанную в параметре конфигурации `LOG_DIR`
```
.
├── log/
│   ├── nginx-access-ui.log-20170630.gz
│   ├── nginx-access-ui.log-20170708.bz2
│   ├── nginx-access-ui.log-20170730
│   └── ...
├── reports/
└── report.html
```
4. Поместите в директорию с отчетами, указанной в параметре конфигурации `REPORT_DIR`, библиотеку [jquery.tablesorter.min.js](https://mottie.github.io/tablesorter/dist/js/jquery.tablesorter.min.js)
5. Войдите в виртуальное окружение
```
poetry shell
```
6. Запустите анализатор
```
python main.py --config <путь/к/файлу/config.json>
```
Результатом работы представленного примера будет созданный файл отчета `report-20170730.html` в директории `reports`
```
.
├── log/
│   ├── nginx-access-ui.log-20170630.gz
│   ├── nginx-access-ui.log-20170708.bz2
│   ├── nginx-access-ui.log-20170730
│   └── ...
├── reports/
│   └── report-20170730.html
└── report.html
```
