# Руководство по развертыванию HorecaBot

## Оглавление

1. [Локальный запуск](#локальный-запуск)
2. [Переменные окружения](#переменные-окружения)
3. [База данных](#база-данных)
4. [Развертывание на VPS](#развертывание-на-vps)
5. [Docker](#docker)
6. [Мониторинг и логирование](#мониторинг-и-логирование)

---

## Локальный запуск

### 1. Установка зависимостей

```bash
# Клонируйте репозиторий
git clone https://github.com/Slava47/telegram-bot-easy.git
cd telegram-bot-easy

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Получение токена бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Сохраните полученный токен

### 3. Создание .env файла

```bash
# Создайте файл .env в корне проекта
touch .env
```

Содержимое `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Веб-панель
ADMIN_LOGIN=admin
ADMIN_PASSWORD=secure_password_here

# База данных (опционально)
DATABASE_URL=sqlite:///horecabot.db

# Redis (опционально)
REDIS_URL=redis://localhost:6379
```

### 4. Запуск бота

```bash
# Используйте один из примеров
python examples/restaurant_example.py
```

---

## Переменные окружения

### Обязательные

| Переменная | Описание | Пример |
|-----------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен от BotFather | `123456:ABC-DEF...` |

### Рекомендуемые

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `ADMIN_LOGIN` | Логин для веб-панели | `admin` |
| `ADMIN_PASSWORD` | Пароль для веб-панели | `admin123` |

### Опциональные

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DATABASE_URL` | URL базы данных | `sqlite:///horecabot.db` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `WEB_PORT` | Порт веб-панели | `5000` |

---

## База данных

### SQLite (для малых проектов)

SQLite используется по умолчанию, не требует настройки.

```python
# Автоматически создастся файл horecabot.db
```

### PostgreSQL (для крупных проектов)

#### Установка PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
```

#### Создание базы данных

```sql
CREATE DATABASE horecabot;
CREATE USER horecabot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE horecabot TO horecabot_user;
```

#### Настройка в .env

```env
DATABASE_URL=postgresql://horecabot_user:your_password@localhost/horecabot
```

---

## Развертывание на VPS

### 1. Выбор хостинга

Рекомендуемые провайдеры:
- **DigitalOcean** (от $5/мес)
- **Linode** (от $5/мес)
- **Vultr** (от $3.5/мес)
- **Hetzner** (от €4/мес)

### 2. Настройка сервера

```bash
# Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# Установка Python 3.8+
sudo apt-get install python3 python3-pip python3-venv -y

# Установка дополнительных пакетов
sudo apt-get install git nginx supervisor -y
```

### 3. Клонирование проекта

```bash
cd /opt
sudo git clone https://github.com/Slava47/telegram-bot-easy.git
cd telegram-bot-easy
```

### 4. Настройка виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Настройка Supervisor

Создайте файл `/etc/supervisor/conf.d/horecabot.conf`:

```ini
[program:horecabot]
command=/opt/telegram-bot-easy/venv/bin/python /opt/telegram-bot-easy/examples/restaurant_example.py
directory=/opt/telegram-bot-easy
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/horecabot.log
environment=TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
```

Запуск:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start horecabot
```

### 6. Настройка Nginx (для веб-панели)

Создайте файл `/etc/nginx/sites-available/horecabot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/horecabot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL сертификат (HTTPS)

```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Docker

### Dockerfile

Создайте `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запуск
CMD ["python", "examples/restaurant_example.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ADMIN_LOGIN=${ADMIN_LOGIN}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/horecabot
    depends_on:
      - db
      - redis
    ports:
      - "5000:5000"
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=horecabot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### Запуск

```bash
# Создайте .env файл с токенами
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

---

## Мониторинг и логирование

### Логи

Логи сохраняются в:
- **Консоль** — во время разработки
- **Файл** — при использовании Supervisor
- **Docker logs** — при использовании Docker

Просмотр логов:

```bash
# Supervisor
sudo tail -f /var/log/horecabot.log

# Docker
docker-compose logs -f bot

# Systemd
sudo journalctl -u horecabot -f
```

### Настройка уровня логирования

```python
import logging

logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR
```

### Мониторинг ресурсов

```bash
# CPU и память
htop

# Процессы Python
ps aux | grep python

# Использование диска
df -h
```

---

## Резервное копирование

### База данных

```bash
# PostgreSQL
pg_dump -U horecabot_user horecabot > backup.sql

# Восстановление
psql -U horecabot_user horecabot < backup.sql
```

### Файлы

```bash
# Создание архива
tar -czf horecabot_backup.tar.gz /opt/telegram-bot-easy

# Восстановление
tar -xzf horecabot_backup.tar.gz -C /opt/
```

---

## Автоматические обновления

### Скрипт обновления

Создайте `update.sh`:

```bash
#!/bin/bash

cd /opt/telegram-bot-easy
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart horecabot
```

Сделайте исполняемым:

```bash
chmod +x update.sh
```

### Cron для автоматического обновления

```bash
# Редактировать crontab
crontab -e

# Обновление каждую ночь в 3:00
0 3 * * * /opt/telegram-bot-easy/update.sh >> /var/log/horecabot_update.log 2>&1
```

---

## Безопасность

### Рекомендации

1. **Токен бота** — никогда не коммитьте в Git
2. **Пароли** — используйте сильные пароли
3. **Firewall** — настройте UFW/iptables
4. **SSH** — отключите вход по паролю
5. **Обновления** — регулярно обновляйте систему

### Настройка Firewall

```bash
# Разрешить SSH
sudo ufw allow 22/tcp

# Разрешить HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включить firewall
sudo ufw enable
```

---

## Решение проблем

### Бот не отвечает

1. Проверьте токен в `.env`
2. Проверьте логи: `sudo tail -f /var/log/horecabot.log`
3. Убедитесь, что процесс запущен: `ps aux | grep python`

### Веб-панель недоступна

1. Проверьте, запущен ли Flask: `netstat -tlnp | grep 5000`
2. Проверьте настройки Nginx: `sudo nginx -t`
3. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`

### Ошибки базы данных

1. Проверьте `DATABASE_URL` в `.env`
2. Убедитесь, что PostgreSQL запущен: `sudo systemctl status postgresql`
3. Проверьте права доступа к БД

---

## Поддержка

При возникновении проблем:
- 📧 Email: support@horecabot.ru
- 💬 Telegram: [@horecabot_support](https://t.me/horecabot_support)
- 🐛 GitHub Issues: [Issues](https://github.com/Slava47/telegram-bot-easy/issues)
