"""
穿搭推薦頁面
提供基於 AI 的智能穿搭建議
"""
import streamlit as st
import base64
import io
from PIL import Image
from api.ai_service import AIService
from api.wardrobe_service import WardrobeService
from api.weather_service import WeatherService
from config import TAIWAN_CITIES

def render_recommendation_page(
    ai_service: AIService,
    wardrobe_service: WardrobeService,
    weather_service: WeatherService,
    user_id: str,
    selected_city: str
):
    """
    渲染穿搭推薦頁面
    
    Args:
        ai_service: AI 服務實例
        wardrobe_service: 衣櫥服務實例
        weather_service: 天氣服務實例
        user_id: 使用者 ID
        selected_city: 選擇的城市
    """
    st.header("今日穿搭推薦")
    
    # 初始化 session state
    if 'ai_recommendation' not in st.session_state:
        st.session_state.ai_recommendation = None
    if 'recommended_items_cache' not in st.session_state:
        st.session_state.recommended_items_cache = None
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    # 城市選擇
    with st.expander("🌍 城市設定", expanded=True):
        city_display = st.selectbox(
            "選擇城市",
            options=list(TAIWAN_CITIES.keys()),
            index=list(TAIWAN_CITIES.values()).index(selected_city) if selected_city in TAIWAN_CITIES.values() else 0,
            help="選擇台灣縣市以獲取天氣資訊",
            key="city_selector"
        )
        
        # 更新選中的城市
        new_city = TAIWAN_CITIES[city_display]
        if new_city != st.session_state.get('selected_city'):
            st.session_state.selected_city = new_city
            st.session_state.weather_data = None  # 清除舊天氣資料
        
        st.caption(f"📍 當前城市: **{new_city}**")
    
    st.divider()
    
    # 使用者輸入區
    col_s, col_o = st.columns(2)
    
    with col_s:
        style_input = st.text_input(
            "🎨 想要什麼風格?",
            placeholder="例如:日系簡約、美式復古...",
            help="留空則由 AI 自由發揮(不限定風格)"
        )
        selected_style = style_input.strip() if style_input.strip() else "不限定風格"
    
    with col_o:
        occasion_input = st.text_input(
            "📍 要去什麼場合/活動?",
            placeholder="例如:公司開會、約會看電影、健身房...",
            help="預設為:外出遊玩"
        )
        selected_occasion = occasion_input.strip() if occasion_input.strip() else "外出遊玩"
    
    st.caption(f"🎯 當前目標:在 **{selected_occasion}** 時,穿出 **{selected_style}**")
    
    # 獲取推薦按鈕
    if st.button("✨ 獲取今日推薦", type="primary", use_container_width=True):
        # 清除舊推薦
        st.session_state.ai_recommendation = None
        st.session_state.recommended_items_cache = None
        st.session_state.carousel_index = 0
        
        # 獲取天氣資料
        with st.spinner("🌤️ 正在查詢天氣..."):
            weather = weather_service.get_weather(st.session_state.selected_city)
        
        if not weather:
            st.error("⚠️ 無法獲取天氣資訊,請檢查 API 設定")
            return
        
        # 獲取衣櫥
        with st.spinner("👔 正在讀取衣櫥..."):
            wardrobe = wardrobe_service.get_wardrobe(user_id)
        
        if not wardrobe:
            st.warning("📦 衣櫥是空的,請先上傳一些衣服!")
            return
        
        st.divider()
        
        # AI 生成推薦
        with st.spinner("🤖 AI 時尚顧問正在為您搭配..."):
            recommendation = ai_service.generate_outfit_recommendation(
                wardrobe=wardrobe,
                weather=weather,
                style=selected_style,
                occasion=selected_occasion
            )
        
        if recommendation:
            st.session_state.ai_recommendation = recommendation
            st.session_state.current_weather = weather
            st.session_state.current_style = selected_style
            st.rerun()
        else:
            st.error("❌ AI 推薦失敗,請重試")
    
    # 顯示推薦結果
    if st.session_state.ai_recommendation:
        st.markdown("### 🎨 今日穿搭建議")
        st.markdown(f"**風格主題:** {st.session_state.current_style}")
        st.divider()
        
        # 顯示 AI 推薦文字
        st.markdown(st.session_state.ai_recommendation)
        
        st.divider()
        
        # 推薦單品展示
        st.markdown("### 👔 推薦單品展示")
        
        # 解析推薦的衣物
        if st.session_state.recommended_items_cache is None:
            wardrobe = wardrobe_service.get_wardrobe(user_id)
            st.session_state.recommended_items_cache = ai_service.parse_recommended_items(
                st.session_state.ai_recommendation,
                wardrobe
            )
        
        recommended_items = st.session_state.recommended_items_cache
        
        if recommended_items:
            # 輪播控制
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ 上一件", key="prev_item", use_container_width=True):
                    st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(recommended_items)
                    st.rerun()
            
            with col2:
                st.markdown(
                    f"<div style='text-align: center; color: #667eea; font-weight: bold; font-size: 18px;'>"
                    f"第 {st.session_state.carousel_index + 1} / {len(recommended_items)} 件"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                if st.button("下一件 ➡️", key="next_item", use_container_width=True):
                    st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(recommended_items)
                    st.rerun()
            
            # 顯示當前衣物
            current_item = recommended_items[st.session_state.carousel_index]
            
            with st.container():
                col_img, col_info = st.columns([3, 2])
                
                with col_img:
                    if current_item.image_data:
                        try:
                            img_bytes = base64.b64decode(current_item.image_data)
                            img = Image.open(io.BytesIO(img_bytes))
                            st.image(img, use_container_width=True)
                        except:
                            st.error("📷 圖片載入失敗")
                    else:
                        st.info("📷 無圖片資料")
                
                with col_info:
                    st.markdown("### 📋 單品資訊")
                    st.markdown(f"**名稱**: {current_item.name or '未命名'}")
                    st.markdown(f"**類別**: {current_item.category or 'N/A'}")
                    st.markdown(f"**顏色**: {current_item.color or 'N/A'}")
                    st.markdown(f"**風格**: {current_item.style or 'N/A'}")
                    st.markdown(f"**保暖度**: {'🔥' * (current_item.warmth or 0)}")
            
            # 快速導航
            st.markdown("---")
            quick_nav_cols = st.columns(len(recommended_items))
            for idx, col in enumerate(quick_nav_cols):
                with col:
                    emoji = "🔵" if idx == st.session_state.carousel_index else "⚪"
                    if st.button(f"{emoji}", key=f"nav_{idx}", use_container_width=True):
                        st.session_state.carousel_index = idx
                        st.rerun()
        else:
            st.info("💡 AI 推薦的衣物未在您的衣櫥中找到對應圖片")
        
        st.success("🎉 穿搭推薦完成! 祝您有美好的一天 ✨")
    
    # 使用說明
    st.divider()
    st.info("""
    **💡 推薦功能說明:**
    - 結合即時天氣與您的衣櫥
    - 考慮 2026 流行趨勢
    - 提供個人化穿搭建議
    - ✨ 顯示推薦衣服的實際圖片
    - 使用 Gemini 2.5 Flash 模型
    """)
