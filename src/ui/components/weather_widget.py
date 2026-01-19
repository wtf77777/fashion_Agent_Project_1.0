"""
天氣小工具組件 - 優化版
只更新天氣區塊,不重新載入整頁
"""
import streamlit as st
from datetime import datetime, timedelta
from api.weather_service import WeatherService
from config import TAIWAN_CITIES

def render_weather_widget(weather_service: WeatherService, current_city: str):
    """
    渲染天氣小工具
    
    Args:
        weather_service: 天氣服務實例
        current_city: 當前城市(英文名稱)
    """
    
    # 初始化狀態
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'weather_update_time' not in st.session_state:
        st.session_state.weather_update_time = None
    if 'weather_city' not in st.session_state:
        st.session_state.weather_city = current_city
    
    # 檢查是否需要更新天氣
    need_update = _check_weather_update_needed(current_city)
    
    # 自動更新天氣
    if need_update:
        with st.spinner("🌤️ 更新天氣中..."):
            weather = weather_service.get_weather(current_city)
            if weather:
                st.session_state.weather_data = weather
                st.session_state.weather_update_time = datetime.now()
                st.session_state.weather_city = current_city
    
    # 顯示天氣資訊
    if st.session_state.weather_data:
        _render_weather_display(current_city)
    else:
        st.warning("⚠️ 無法獲取天氣資料")


def _check_weather_update_needed(current_city: str) -> bool:
    """
    檢查是否需要更新天氣
    
    Returns:
        是否需要更新
    """
    # 情況 1: 沒有天氣資料
    if st.session_state.weather_data is None:
        return True
    
    # 情況 2: 城市改變了
    if st.session_state.weather_city != current_city:
        return True
    
    # 情況 3: 超過 1 小時沒更新
    if st.session_state.weather_update_time:
        time_diff = datetime.now() - st.session_state.weather_update_time
        if time_diff > timedelta(hours=1):
            return True
    
    return False


def _render_weather_display(current_city: str):
    """
    渲染天氣顯示區塊
    
    Args:
        current_city: 當前城市
    """
    weather = st.session_state.weather_data
    
    # 使用 container 讓天氣區塊可以局部更新
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"### 🌍 {current_city} 即時天氣")
        
        with col2:
            st.metric("🌡️ 溫度", f"{weather.temp}°C")
        
        with col3:
            st.metric("🤚 體感", f"{weather.feels_like}°C")
        
        with col4:
            st.metric("☁️ 天氣", weather.desc)
        
        # 顯示更新時間
        if st.session_state.weather_update_time:
            update_time = st.session_state.weather_update_time.strftime("%H:%M")
            st.caption(f"⏰ 更新時間: {update_time} (每小時自動更新)")
    
    st.divider()


def render_city_selector():
    """
    渲染城市選擇器(用於推薦頁面)
    
    Returns:
        選中的城市英文名稱
    """
    # 找出當前城市的顯示名稱
    current_city = st.session_state.get('selected_city', 'Taipei')
    
    # 找出對應的顯示名稱
    current_display = "台北 (Taipei)"
    for display, english in TAIWAN_CITIES.items():
        if english == current_city:
            current_display = display
            break
    
    # 渲染選擇器
    with st.expander("🌍 城市設定", expanded=True):
        city_display = st.selectbox(
            "選擇城市", 
            options=list(TAIWAN_CITIES.keys()),
            index=list(TAIWAN_CITIES.keys()).index(current_display),
            help="選擇台灣縣市以獲取天氣資訊",
            key="city_selector_widget"
        )
        
        # 轉換為英文名稱
        selected_city = TAIWAN_CITIES[city_display]
        
        # 只在城市改變時更新 session state
        if st.session_state.get('selected_city') != selected_city:
            st.session_state.selected_city = selected_city
            # 清除天氣快取,強制重新獲取
            st.session_state.weather_data = None
            st.session_state.weather_city = None
            # 🔥 使用 rerun 只更新天氣區塊
            st.rerun()
        
        st.caption(f"📍 當前城市: **{selected_city}**")
    
    return selected_city
