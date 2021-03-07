# Скрипт для удобного сбора и переименования файлов с меню для размещения на сайте ОУ

## Инструкция по установке и использованию

1. Склонировать репозиторий себе
```shell
    git clone https://github.com/dzenbots/menu_from_mail.git
```
2. Установить все библиотеки для работы со скриптом
```shell
    pip install -r requirements.txt
```

3. Создать файл с именем *.env* со следующим содержимым
```dotenv
    LOGIN = 'your@email.ru'
    PASSWORD = 'your_password'
    IMAP_SERVER = 'imap.email.ru'
    DIRECTORY_TO_SAVE_FILES = './Menus'
    MENU_FOLDER_NAME = 'Меню'
```

4. Запустить файл *start_app.py* 
```shell
    python start_app.py
```