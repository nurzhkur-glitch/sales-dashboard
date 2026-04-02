# Sales Analytics Dashboard

Streamlit-дашборд для аналитики продаж, заменяющий Power BI.

## Возможности

- **5 страниц**: Обзор, Филиалы, Категории, Сотрудники, Сравнение и прогноз
- **Авто-инсайты** на основе данных
- **Гибкие фильтры**: период, филиал, категория, источник, сотрудник
- **Сравнение периодов**: месяц к месяцу, год к году
- **Прогноз** на основе линейной регрессии
- **Алерты** при отклонении метрик
- **Экспорт в PDF**

## Быстрый старт (локально)

### 1. Установка зависимостей

```bash
cd 3_analitica
pip install -r requirements.txt
```

### 2. Настройка Google API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект (или выберите существующий)
3. Включите **Google Sheets API** и **Google Drive API**
4. Перейдите в **APIs & Services → Credentials**
5. Нажмите **Create Credentials → Service Account**
6. Скачайте JSON-ключ сервисного аккаунта
7. Откройте каждую из 3-х Google Sheets и расшарьте на email сервисного аккаунта (из JSON-файла, поле `client_email`) с правами **Viewer**

### 3. Настройка secrets

Создайте файл `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

Скопируйте все поля из скачанного JSON-ключа.

### 4. Запуск

```bash
streamlit run app.py
```

Откроется в браузере: `http://localhost:8501`

## Деплой на Streamlit Cloud (бесплатно)

1. Создайте репозиторий на GitHub и пушните проект
2. Перейдите на [share.streamlit.io](https://share.streamlit.io)
3. Нажмите **New app** → укажите ваш репозиторий
4. В **Advanced settings → Secrets** вставьте содержимое `secrets.toml`
5. Нажмите **Deploy**

Дашборд будет доступен по ссылке вида `https://your-app.streamlit.app`

## Структура проекта

```
app.py                    — главный файл (навигация + фильтры)
pages/
  1_overview.py           — Обзор: KPI, графики, таблица
  2_branches.py           — Филиалы: сравнение, heatmap
  3_categories.py         — Категории: доли, динамика
  4_employees.py          — Сотрудники: рейтинг, профиль
  5_comparison.py         — Сравнение периодов + прогноз
utils/
  data_loader.py          — загрузка из Google Sheets
  charts.py               — графики Plotly
  insights.py             — авто-инсайты
  styles.py               — стили и CSS
  export.py               — экспорт в PDF
.streamlit/
  config.toml             — тема
  secrets.toml            — ключи (не коммитить!)
```

## Google Sheets

| Таблица | ID | Содержание |
|---|---|---|
| excel_employee_2025 | `1P1pXtdiVRyhSMKcN0YFz9vky4Y2Hk-5eS062Eyuovwc` | Сотрудник → ID продажи |
| excel_sale_2025 | `164NMj0zKihkwGgViQ56mG4HkDvofnU2ZIzAOTMoCQgU` | Продажи (цены, категории, филиалы) |
| excel_source_2025 | `1QWh3JwvNU9k-bMDG1fKe9Q7njCegO6tcZsngQO76a8Y` | Источник товара (скупка/залог) |
