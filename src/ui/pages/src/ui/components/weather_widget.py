"""
天氣小工具組件
顯示即時天氣資訊,支援自動更新
"""
import streamlit as st
from datetime import datetime, timedelta
from api.weather_service import WeatherService

def render_weather_widget(weather_service: WeatherService, current_city: str):
    """
    渲染天氣小工具
    
    Args:
        weather_service: 天氣服務實例
        current_city: 當前選擇的城市
    """
    # 初始化 session state
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'weather_update_time' not in st.session_state:
        st.session_state.weather_update_time = None
    
    weather_container = st.container()
    
    with weather_container:
        # 檢查是否需要更新天氣
        now = datetime.now()
        need_update = False
        
        if st.session_state.weather_data is None:
            need_update = True
        elif st.session_state.weather_update_time is None:
            need_update = True
        elif (now - st.session_state.weather_update_time) > timedelta(hours=1):
            need_update = True
        
        # 更新天氣資料
        if need_update:
            with st.spinner("🌤️ 正在獲取天氣資訊..."):
                weather = weather_service.get_weather(current_city)
                if weather:
                    st.session_state.weather_data = weather
                    st.session_state.weather_update_time = now
        
        # 顯示天氣資訊
        if st.session_state.weather_data:
            weather = st.session_state.weather_data
            
            # 使用四欄佈局
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"### 🌍 {current_city} 即時天氣")
            
            with col2:
                st.metric("🌡️ 溫度", f"{weather.temp}°C")
            
            with col3:
                st.metric("😊 體感", f"{weather.feels_like}°C")
            
            with col4:
                st.metric("☁️", weather.desc)
            
            # 顯示更新時間
            if st.session_state.weather_update_time:
                update_time = st.session_state.weather_update_time.strftime("%H:%M")
                st.caption(f"⏰ 更新時間: {update_time} (每小時自動更新)")
            
            st.divider()
        else:
            st.warning("⚠️ 無法獲取天氣資訊,請檢查 API 設定")
