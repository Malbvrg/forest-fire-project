# 🔥 Прогноз лесных пожаров

Проект посвящен природным пожарам - преимущественно лесным и степным. Отображаются точки пожаров на карте, и строится прогноз "если пожар начинается при заданных температурных условиях, какова его ожидаемая продолжительность и площадь?"
Набор данных о пожарах - https://tochno.st/datasets/fires, статистическая форма 1T-ИСДМ (Реестр природных пожаров), период - 2000-2024 гг.
Набор погодных данных - http://aisori-m.meteo.ru/, 8-срочные наблюдения на 134 российских метеостанциях: средняя скорость ветра, средняя температура воздуха между сроками, сумма осадков.
Набор координат метеостанций - https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily, Stations.txt
Данные конвертированы в Parquet.

Бэкенд: api/main.py, src/models.py, requirements.txt
Фронтенд: app.py
Датасеты: data/data_fires.csv, data/data_weather.csv, data/data_merged.csv, data/data_merged.parquet

Локальный запуск: 

1. Клонировать репозиторий:
git clone https://github.com/Malbvrg/forest-fire-project.git
2. Зайти в папку проекта:
cd forest_fire_project

3. Создать и активировать виртуальное окружение:
python -m venv venv
venv\Scripts\activate

4. Установить зависимости:
pip install -r requirements.txt

5. Запустить сервер с моделью (в первом терминале):
uvicorn api.main:app --host 0.0.0.0 --port 8000

6. Запустить приложение Streamlit (во втором терминале):
streamlit run app.py