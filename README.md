# SetProductScoring
Выбор товаров и установка пометки о необходимости проценки 

### Описание

------------
Скрипт для установки выбранных товаров для дальнейшего получения цены от поставщиков

Данный скрипт получает информацию о позициях из Google таблицы.
В таблице 11 колонок с данными.

`Каталожный номер`,	`Бренд`, `Описание`, `Наличие`, `Цена`, `дата проценки`, `коэф оборачиваемости`,
`норма наличия`, `правило проценки товара`, `отбор для проценки`, `ID выбранное правило проценки`

Скрипт выбирает позиции согласно правилам и в колонке `10` устанавливает `1` если позиция 
удовлетворяет правилам и очищает значение в этой колонке, если позиция не была выбрана.

Для работы с google таблицей требуется создать сервисный аккаунт google.
[Инструкция по созданию google аккаунта](https://dvsemenov.ru/google-tablicy-i-python-podrobnoe-rukovodstvo-s-primerami/)

### Доступы

------------

Данные для доступа размещаем в файл config.py:    
```python
AUTH_GOOGLE: dict = {
    'GOOGLE_CLIENT_ID': 'ваш google клиент id',
    'GOOGLE_CLIENT_SECRET': 'ваш google ',
    'KEY_WORKBOOK': 'id вашей google таблицы'
}
FILE_NAME_LOG: str = 'имя вашего лог файла'
```
Так же в папке проекта [services/google_table](services/google_table) необходимо расположить файл 
`credentials.json` с параметрами подключения к Google таблице
Подробная инструкция по настройке работы с Google таблицами по 
[ссылке](https://dvsemenov.ru/google-tablicy-i-python-podrobnoe-rukovodstvo-s-primerami/)
Содержимое файла:
```python
{
  "type": "service_account",
  "project_id": "ваше наименование проeкта",
  "private_key_id": "ваш id",
  "private_key": "ваш ключ",
  "client_email": "email вашего сервиса, который добавляется как редактор к google таблице",
  "client_id": "id вашего сервиса",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "url сертификата вашего сервиса",
  "universe_domain": "googleapis.com"
}
```

### Примечание 

------------
Для логирования используется библиотека [logguru](https://loguru.readthedocs.io/en/stable/overview.html)
Наименование лог файла прописывается в файле config.py в переменную `FILE_NAME_LOG`