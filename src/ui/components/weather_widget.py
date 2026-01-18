"""
天氣小工具組件 - 性能優化版
顯示即時天氣資訊,支援智能快取與自動更新
"""
import streamlit as st
from datetime import datetime, timedelta
from api.weather_service import WeatherService

@st.cache_data(ttl=3600, show_spinner=False)  # ✅ 快取 1 小時
def fetch_weather_cached(city: str, api_key: str):
    """
    快取天氣資料獲取
    
    Args:
        city: 城市名稱
        api_key: API Key
        
    Returns:
        天氣資料字典或 None
    """
    from api.weather_service import WeatherService
    service = WeatherService(api_key)
    weather = service.get_weather(city)
    
    if weather:
        return weather.to_dict()
    return None

def render_weather_widget(weather_service: WeatherService, current_city: str):
    """
    渲染天氣小工具 - 優化版
    
    Args:
        weather_service: 天氣服務實例
        current_city: 當前選擇的城市
    """
    weather_container = st.container()
    
    with weather_container:
        # ✅ 使用快取獲取天氣
        weather_dict = fetch_weather_cached(current_city, weather_service.api_key)
        
        if weather_dict:
            # 使用四欄佈局
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"### 🌍 {current_city} 即時天氣")
            
            with col2:
                st.metric("🌡️ 溫度", f"{weather_dict['temp']}°C")
            
            with col3:
                st.metric("😊 體感", f"{weather_dict['feels_like']}°C")
            
            with col4:
                st.metric("☁️", weather_dict['desc'])
            
            # 顯示快取時間
            st.caption("⏰ 資料每小時自動更新")
            
            st.divider()
        else:
            st.warning("⚠️ 無法獲取天氣資訊,請檢查 API 設定")
