import streamlit as st
import requests

# Use Streamlit secrets online and api_key.py on your computer
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    from api_key import API_KEY


# Set up the app
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="checkweatherr.PNG",
    layout="wide"
)

st.title("🌦️ Weather Forecast App")
st.write("Check current weather, rain chances, and upcoming forecasts.")

# List of cities
cities = [
    "Karachi",
    "Lahore",
    "Islamabad",
    "Peshawar",
    "Quetta",
    "London",

    # 10 additional international cities
    "Beijing, China",
    "Shanghai, China",
    "Guangzhou, China",
    "Shenzhen, China",
    "Tokyo, Japan",
    "Seoul, South Korea",
    "Dubai, UAE",
    "Paris, France",
    "New York, USA",
    "Sydney, Australia"
]

city = st.selectbox("Select a city:", cities)

if st.button("Get Weather", type="primary"):

    current_url = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    parameters = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        # Get current weather
        current_response = requests.get(
            current_url, params=parameters, timeout=10
        )

        # Get forecast
        forecast_response = requests.get(
            forecast_url, params=parameters, timeout=10
        )

        if current_response.status_code == 200 and forecast_response.status_code == 200:

            current = current_response.json()
            forecast = forecast_response.json()

            # Current weather details
            temperature = current["main"]["temp"]
            feels_like = current["main"]["feels_like"]
            humidity = current["main"]["humidity"]
            pressure = current["main"]["pressure"]
            description = current["weather"][0]["description"].title()
            wind_speed = current["wind"]["speed"]
            clouds = current["clouds"]["all"]

            st.header(f"Weather in {city}")
            st.write(f"**Conditions:** {description}")

            # Display weather information in columns
            col1, col2, col3 = st.columns(3)

            col1.metric("🌡️ Temperature", f"{temperature} °C")
            col2.metric("🤔 Feels Like", f"{feels_like} °C")
            col3.metric("💧 Humidity", f"{humidity}%")

            col4, col5, col6 = st.columns(3)

            col4.metric("💨 Wind Speed", f"{wind_speed} m/s")
            col5.metric("☁️ Cloud Cover", f"{clouds}%")
            col6.metric("🧭 Pressure", f"{pressure} hPa")

            # Prepare the next 24 hours of forecast data
            forecast_list = forecast["list"][:8]

            times = []
            temperatures = []
            rain_chances = []
            rainfall = []

            for item in forecast_list:
                # Forecast time
                time = item["dt_txt"]
                times.append(time[5:16])

                # Forecast temperature
                temperatures.append(item["main"]["temp"])

                # Probability of precipitation
                rain_chances.append(item.get("pop", 0) * 100)

                # Rain volume forecast for a 3-hour period
                rain_data = item.get("rain", {})
                rainfall.append(rain_data.get("3h", 0))

            st.subheader("🌧️ Rain Forecast")

            max_rain_chance = max(rain_chances)
            total_rain = sum(rainfall)

            rain_col1, rain_col2 = st.columns(2)

            rain_col1.metric(
                "Highest Rain Probability",
                f"{max_rain_chance:.0f}%"
            )

            rain_col2.metric(
                "Forecast Rainfall Total",
                f"{total_rain:.1f} mm"
            )

            st.caption(
                "Forecast covers approximately the next 24 hours "
                "in 3-hour intervals. Rainfall is an estimate."
            )

            # Rain precipitation graph
            st.subheader("📈 Expected Rainfall")

            st.line_chart(
                {
                    "Rainfall (mm per 3 hours)": rainfall
                },
                x_label="Forecast interval",
                y_label="Rainfall (mm)"
            )

            # Rain probability graph
            st.subheader("☔ Chance of Rain")

            st.line_chart(
                {
                    "Rain probability (%)": rain_chances
                },
                x_label="Forecast interval",
                y_label="Probability (%)"
            )

            # Temperature graph
            st.subheader("🌡️ Temperature Forecast")

            st.line_chart(
                {
                    "Temperature (°C)": temperatures
                },
                x_label="Forecast interval",
                y_label="Temperature (°C)"
            )

            # Detailed forecast table
            st.subheader("🕒 Upcoming Forecast")

            forecast_rows = []

            for index, item in enumerate(forecast_list):
                forecast_rows.append({
                    "Time": times[index],
                    "Temperature (°C)": round(temperatures[index], 1),
                    "Conditions": item["weather"][0]["description"].title(),
                    "Rain Chance (%)": round(rain_chances[index]),
                    "Rainfall (mm/3h)": round(rainfall[index], 1),
                    "Humidity (%)": item["main"]["humidity"],
                    "Wind (m/s)": item["wind"]["speed"],
                    "Cloud Cover (%)": item["clouds"]["all"]
                })

            st.dataframe(
                forecast_rows,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.error(
                "Could not retrieve weather data. "
                "Check your API key, internet connection, "
                "or OpenWeatherMap API access."
            )

            st.write("Current weather status:", current_response.status_code)
            st.write("Forecast status:", forecast_response.status_code)

    except requests.exceptions.RequestException:
        st.error("Network error. Please check your internet connection.")
