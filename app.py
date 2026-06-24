import streamlit as st
import requests
import calendar
import pandas as pd
import os

API_URL = "http://localhost:8000/predict"

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="🔥 Прогноз пожаров + Карта", layout="wide")
st.title("🔥 Прогноз лесных пожаров")
st.caption("Выберите дату и погодные условия (слева) / Изучите историю пожаров на карте (справа)")

data_path = "data/data_merged.parquet"

# Проверка существования файла
if not os.path.exists(data_path):
    st.error(f"❌ Файл не найден: {data_path}")
    st.info("Пожалуйста, создайте папку 'data' в корне проекта и положите туда файл 'data_merged.parquet'.")
    # Останавливаем выполнение скрипта, чтобы не было ошибок ниже
    st.stop()

try:
    df_map = pd.read_parquet(data_path)

    df_map = df_map.drop(columns=['oktmo', 'okato', 'type', 'code', 'zone_beginning',
       'landmark_azimuth', 'landmark_distance', 'date_end', 'current_state', 'area_total',
       'area_fund_total', 'area_fund_forest', 'comment', 'zone', 'date_liquidation','geometry',
       'index_right', 'Синоптический индекс станции', 'latitude_right', 'longitude_right', 
       'Station name', 'distance_m', 'date', 'temp_3d_lag', 'wind_3d_max_lag', 'rain_7d_sum_lag'])
    
    # Нормализация названий колонок (на всякий случай приводим к нижнему регистру и убираем пробелы)
    df_map.columns = df_map.columns.str.strip().str.lower()
    
    # Проверка обязательных колонок
    required_cols = ['year', 'latitude_left', 'longitude_left']
    missing_cols = [col for col in required_cols if col not in df_map.columns]
    
    if missing_cols:
        st.error(f"⚠️ В файле отсутствуют необходимые колонки: {', '.join(missing_cols)}")
        st.info("Убедитесь, что в CSV есть колонки: year, latitude, longitude (или lat, lon).")
        st.stop()
        
    # Переименовываем широту и долготу для st.map
    if 'latitude_left' in df_map.columns and 'latitude' not in df_map.columns:
        df_map = df_map.rename(columns={'latitude_left': 'latitude'})
    if 'longitude_left' in df_map.columns and 'longitude' not in df_map.columns:
        df_map = df_map.rename(columns={'longitude_left': 'longitude'})

except Exception as e:
    st.error(f"❌ Ошибка при чтении файла: {e}")
    st.stop()

# --- РАЗДЕЛЕНИЕ НА КОЛОНКИ ---
col_left, col_right = st.columns([1, 2])

# ================= ЛЕВАЯ КОЛОНКА (ПРОГНОЗ) =================
with col_left:
    with st.form("fire_form"):
        col_date_1, col_date_2 = st.columns(2)
        
        month = col_date_1.selectbox("Месяц", list(range(1, 13)), index=5) # Июнь по умолчанию (индекс 5, т.к. список с 1)
        day = col_date_2.number_input("День месяца (1–31)", min_value=1, max_value=31, value=15, step=1)
        
        is_date_valid = False
        day_of_year = 0
        error_msg = ""

        try:
            _, days_in_month = calendar.monthrange(2024, month)
            if 1 <= day <= days_in_month:
                is_date_valid = True
                day_of_year = sum(calendar.monthrange(2024, m) for m in range(1, month)) + day
            else:
                error_msg = f"⚠️ В выбранном месяце максимум {days_in_month} дней!"
        except Exception:
            error_msg = "❌ Ошибка в дате"

        if not is_date_valid and error_msg:
            st.error(error_msg)

        col3, col4 = st.columns(2)
        temp_3d = col3.number_input("Средняя темп. за 3 дня до (°C)", value=28.5, format="%.1f")
        wind = col4.number_input("Макс. ветер за 3 дня (м/с)", value=12.3, format="%.1f")
        rain_7d = st.number_input("Осадки за 7 дней (мм)", value=5.2, format="%.1f")

        submitted_btn = st.form_submit_button("Рассчитать прогноз", type="primary", disabled=not is_date_valid)

        if submitted_btn and is_date_valid:
            payload = {
                "month": month,
                "day_of_year": day_of_year,
                "temp_3d_lag": temp_3d,
                "wind_3d_max_lag": wind,
                "rain_7d_sum_lag": rain_7d,
            }

            with st.spinner("Обрабатываем запрос..."):
                try:
                    resp = requests.post(API_URL, json=payload, timeout=10)
                    resp.raise_for_status()
                    result = resp.json()

                    st.success("✅ Прогноз успешно получен!")
                    st.metric("Ожидаемая длительность", f"{result['pred_duration_days']:.1f} дней")

                    if result.get("area_is_small", False):
                        st.info("⚠️ Ожидаемая площадь меньше 1 гектара")
                    else:
                        st.metric("Ожидаемая площадь", f"{result['pred_area_ha']:.1f} га")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Ошибка соединения! Проверьте, запущен ли FastAPI.")
                except Exception as e:
                    st.error(f"❌ Произошла ошибка: {e}")

# ================= ПРАВАЯ КОЛОНКА (КАРТА И СЛАЙДЕР) =================
with col_right:
    st.subheader("🗺️ История пожаров")
    
    if not df_map.empty:
        min_year = int(df_map['year'].min())
        max_year = int(df_map['year'].max())
        
        selected_year = st.slider("Выберите год", min_value=min_year, max_value=max_year, value=min_year, step=1)
        
        df_filtered = df_map[df_map['year'] == selected_year]
        
        if not df_filtered.empty:
            st.write(f"Найдено пожаров в {selected_year} году: **{len(df_filtered)}**")
            st.map(df_filtered, zoom=4)
            
            with st.expander("Показать данные за этот год"):
                st.dataframe(df_filtered, hide_index=True)
        else:
            st.warning("В этом году в датасете нет записей.")
    else:
        st.warning("Датасет пуст.")
