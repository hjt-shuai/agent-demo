import httpx
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气，输入城市名，返回当前天气信息"""
    try:
        resp = httpx.get(
            f"https://wttr.in/{city}?format=j1&lang=zh",
            timeout=15,
        )
        if resp.status_code != 200:
            return f"查询天气失败：HTTP {resp.status_code}"

        data = resp.json()
        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]
        city_name = area.get("areaName", [{}])[0].get("value", city)
        weather_desc = current.get("weatherDesc", [{}])[0].get("value", "未知")

        return (
            f"📍 {city_name} 实时天气\n"
            f"🌡 温度：{current.get('temp_C', '?')}°C（体感 {current.get('FeelsLikeC', '?')}°C）\n"
            f"☁ 天气：{weather_desc}\n"
            f"💧 湿度：{current.get('humidity', '?')}%\n"
            f"💨 风向：{current.get('winddir16Point', '?')}，风速 {current.get('windspeedKmph', '?')}km/h\n"
            f"👀 能见度：{current.get('visibility', '?')}km"
        )
    except Exception as e:
        return f"查询天气时出错：{str(e)}"
