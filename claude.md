# Claude — Документация для AI-ассистента

## Контекст проекта

Это Streamlit-дашборд для аналитики продаж розничной сети в Алматы (Казахстан). Бизнес продаёт ювелирные изделия, телефоны, ноутбуки, smart часы и аксессуары через 16+ филиалов. Дашборд заменяет Power BI.

## Файловая структура

```
3_analitica/
├── app.py                      # Точка входа: навигация + фильтры в сайдбаре
├── pages/
│   ├── 1_overview.py           # Обзор: KPI, графики, годовая таблица, PDF-экспорт
│   ├── 2_branches.py           # Филиалы: bar chart, heatmap, тренды
│   ├── 3_categories.py         # Категории: donut, динамика, топ-товары
│   ├── 4_employees.py          # Сотрудники: рейтинг, профиль, KPI
│   └── 5_comparison.py         # Сравнение MoM/YoY, прогноз, алерты
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # Загрузка из Google Sheets (CSV-экспорт), JOIN, очистка
│   ├── charts.py               # Plotly-графики: line, bar, donut, heatmap, forecast
│   ├── insights.py             # Генерация авто-инсайтов и алертов
│   ├── styles.py               # Кастомный CSS, KPI-карточки, форматирование чисел
│   └── export.py               # Генерация PDF-отчёта
├── deploy/
│   └── setup.sh                # Скрипт деплоя на Ubuntu-сервер
├── .streamlit/
│   └── config.toml             # Тёмная тема, цвета, шрифт
├── .gitignore
├── requirements.txt
├── README.md                   # Инструкция для пользователя
├── plan.md                     # План проекта, архитектура, backlog
└── claude.md                   # Этот файл — контекст для AI
```

## Ключевые решения и почему

### Загрузка данных (data_loader.py)
- **Публичный CSV-экспорт** вместо Google API — не нужны ключи, таблицы публичные
- **dtype=str** в `pd.read_csv()` — Google Sheets использует неразрывные пробелы (U+00A0) как разделители тысяч. Без `dtype=str` pandas автоматически определяет типы и ломает числа на серверах с другой локалью (Streamlit Cloud)
- **_clean_numeric()** — явно удаляет U+00A0, пробелы, запятые перед конвертацией в числа
- **Кэш ttl=3600** — данные обновляются раз в неделю, кэш на 1 час достаточен
- **JOIN по ID** — три таблицы объединяются в один DataFrame через нормализованный ID (lowercase, strip)

### Архитектура страниц
- **app.py** загружает данные, строит фильтры и сохраняет отфильтрованный DataFrame в `st.session_state`
- Каждая страница читает `st.session_state["filtered_df"]` и `st.session_state["full_df"]`
- Инсайты используют `full_df` (нефильтрованные данные) для корректного сравнения периодов

### Стили
- Тёмная тема с фиолетовым акцентом (#6C5CE7)
- Кастомные CSS-карточки для KPI через `div[data-testid="stMetric"]`
- Insight-карточки с цветной левой границей (success/warning/danger/info)

## Данные

### Источники
- **excel_sale_2025** (ID: 164NMj0zKihkwGgViQ56mG4HkDvofnU2ZIzAOTMoCQgU) — основная таблица продаж
- **excel_employee_2025** (ID: 1P1pXtdiVRyhSMKcN0YFz9vky4Y2Hk-5eS062Eyuovwc) — сотрудники
- **excel_source_2025** (ID: 1QWh3JwvNU9k-bMDG1fKe9Q7njCegO6tcZsngQO76a8Y) — источник товара

### Колонки основной таблицы (после обработки)
`id`, `наименование`, `дата` (datetime), `наценка` (float), `себестоимость` (float), `витрина` (float), `продажа` (float), `подкатегория` (str), `состояние` (str), `отделение` (str), `комментарий` (str), `сотрудник` (str), `источник` (str), `маржа_%` (float), `год` (int), `месяц` (int), `неделя` (int)

### Подкатегории
Ювелирные изделия (~55%), Телефоны (~38%), Ноутбуки и нетбуки (~5%), Smart часы (~1%), Аксессуары (<1%), Другое (<1%)

### Филиалы (отделения)
L'amour, L'amour NEW, L'amour KASPI, ReTech, Ком. магазин, Service, Айнабулак, Аксай, Толе Би, Мира, Арыстан, Шолохова, Алмагуль, Арена, Самал, Сахат, Склад Тов, Rent

## Деплой

- **Streamlit Cloud**: https://sales-dashboard-99pkhd3rtquur6rxsfmzuh.streamlit.app/
- **GitHub** (для Streamlit Cloud): https://github.com/nurzhkur-glitch/sales-dashboard
- **GitLab** (основной): https://gitlab.technation.kz/n.kurmangaliev/sales-dashboard
- Push в GitHub main → автоматический деплой на Streamlit Cloud

## Известные проблемы и решения

| Проблема | Причина | Решение |
|---|---|---|
| Числа = 0 на Streamlit Cloud | Неразрывные пробелы U+00A0 в CSV из Google Sheets | `dtype=str` + явная очистка в `_clean_numeric()` |
| Данные только за 2025-2026 | Google Sheets содержат только этот период | Нужно добавить дополнительные таблицы за 2018-2024 |
| Кэш не обновляется | ttl=3600 (1 час) | Меню ⋮ → Clear cache, или уменьшить ttl |

## Как вносить изменения

1. Редактировать файлы в `3_analitica/`
2. Проверить локально: `streamlit run app.py`
3. Закоммитить и запушить:
```bash
git add -A && git commit -m "описание" && git push github main
```
4. Streamlit Cloud подхватит через 1-2 минуты
5. Если нужен мгновенный перезапуск: на сайте ⋮ → Reboot app
