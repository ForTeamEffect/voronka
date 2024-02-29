# EORA 
- https://t.me/esusincep1983 - client-бот
- This project is a telegram bot created using Python==3.10.11.
- я - https://t.me/Sudokuh

# Installation

1. Clone the repository

```
If you don't use Git, you can simply download the repository source code in a ZIP archive and extract it to your computer.
```

2. Create a virtual environment and activate it

```
python -m venv venv
for Mac
source venv/bin/activate
or
for Win
source venv/Skripts/activate
```

3. create .env

4. Install dependencies

```
pip install -r requirements.txt
```

5. settings:

+ установите postgreSQL, если нету.

+ создать и заполнить .env по шаблону:
+ пройдите по адресу https://my.telegram.org/auth и возьмите данные своего client
```
postgreSQL
PG_USER = 'your_username'
PG_PASSWORD = 'your_password'
PG_ADDRESS = 'localhost'
PG_PORT = '5432'
PG_SERVER_NAME = 'eora'


telegram
API_ID_1 = "22979979",
API_HASH_1 = "34c33fa9f295b...",
PHONE_NUMBER_1 = "+66993579..."

```

6. Start

+ python main.py

Ready!
You have successfully installed the bot and are ready to start using it!

# Улучшения, которые могут быть:

1. данный код подразумевает возможность запуска нескольких аккаунтов. Для того чтобы это работало, как надо - дополнить список в data/accounts.py и сделать доп. связи с каждым нашим аккаунтом в БД, чтобы несколько аккаунтов не писали одному и тому же клиенту.
2. время отправки, которое указано в texts_plus_time_of_await.py указано для теста, уберите комментирование первой версии messages_from_states, чтобы соответствовало тз.

# Contribution to the project

If you have suggestions for improvement or find a bug, feel free to create an issue, send a pull request, or write
directly to the author. Your input is welcome!
#Author
[Diashov Makar](https://github.com/ForTeamEffect)