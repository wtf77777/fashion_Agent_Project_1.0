"""
主應用入口
只負責頁面路由和狀態管理,所有業務邏輯已分離
"""
import streamlit as st
from config import AppConfig, TAIWAN_CITIES, get_city_display_name
from database.supabase_client import SupabaseClient
from api.ai_service import AIService
from api.wardrobe_service import WardrobeService
from api.weather_service import WeatherService
from ui.components.weather_widget import render_weather_widget
from ui.pages.upload_page import render_upload_page
from ui.pages.wardrobe_page import render_wardrobe_page
from ui.pages.recommendation_page import render_recommendation_page
from ui.styles import apply_custom_styles

# 頁面配置
st.set_page_config(
    page_title="2026 AI 時尚顧問", 
    page_icon="☁️",
    layout="wide"
)

# 應用自定義樣式
from ui.styles import apply_custom_styles, render_scroll_to_top_button
apply_custom_styles()

# 渲染回到頂端按鈕（放在最開始）
render_scroll_to_top_button()

def init_session_state():
    """初始化 Session State"""
    if 'config' not in st.session_state:
        # 優先使用 Secrets,否則使用環境變數
        config = AppConfig.from_secrets()
        if config is None:
            config = AppConfig.from_env()
        st.session_state.config = config
    
    if 'supabase_client' not in st.session_state:
        st.session_state.supabase_client = None
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = st.session_state.config.default_city
    
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    
    if 'ai_recommendation' not in st.session_state:
        st.session_state.ai_recommendation = None

def render_sidebar():
    """渲染側邊欄"""
    with st.sidebar:
        st.header("🔑 API 設定")
        
        config = st.session_state.config
        
        if config.is_valid():
            st.success("✅ 使用雲端設定")
            st.caption("API Keys 已從安全儲存處載入")
        else:
            st.info("💡 本地模式: 請輸入 API Keys")
            config.gemini_api_key = st.text_input("Gemini API Key", type="password")
            config.weather_api_key = st.text_input("OpenWeather Key", type="password")
            config.supabase_url = st.text_input("Supabase URL")
            config.supabase_key = st.text_input("Supabase Anon Key", type="password")
        
        # 連接 Supabase
        if config.supabase_url and config.supabase_key:
            if st.session_state.supabase_client is None:
                try:
                    st.session_state.supabase_client = SupabaseClient(
                        config.supabase_url, 
                        config.supabase_key
                    )
                    st.success("✅ Supabase 已連接")
                except Exception as e:
                    st.error(f"❌ Supabase 連接失敗: {str(e)}")
        
        st.divider()
        
        # 使用者資訊
        if st.session_state.user_id:
            st.success(f"👤 目前使用者: **{st.session_state.username}**")
            
            if st.button("🚪 登出", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.weather_data = None
                st.session_state.ai_recommendation = None
                st.rerun()

def render_login():
    """渲染登入/註冊頁面"""
    st.info("👋 請先登入或註冊以使用個人衣櫥")
    
    tab_login, tab_register = st.tabs(["🔒 登入", "📝 註冊"])
    
    with tab_login:
        with st.form("login_form"):
            st.subheader("登入帳號")
            username = st.text_input("使用者名稱", key="login_user")
            password = st.text_input("密碼", type="password", key="login_pass")
            
            if st.form_submit_button("登入", use_container_width=True):
                if not st.session_state.supabase_client:
                    st.error("請先在左側設定 Supabase 連接")
                elif not username or not password:
                    st.warning("請輸入使用者名稱和密碼")
                else:
                    # 這裡應該呼叫 AuthService
                    # 為了簡化,暫時直接操作資料庫
                    try:
                        result = st.session_state.supabase_client.client.table("users")\
                            .select("*")\
                            .eq("username", username)\
                            .eq("password", password)\
                            .execute()
                        
                        if result.data:
                            st.session_state.user_id = result.data[0]['id']
                            st.session_state.username = username
                            st.success(f"歡迎回來, {username}! 🎉")
                            st.rerun()
                        else:
                            st.error("帳號或密碼錯誤")
                    except Exception as e:
                        st.error(f"登入失敗: {str(e)}")
    
    with tab_register:
        with st.form("register_form"):
            st.subheader("註冊新帳號")
            username = st.text_input("使用者名稱", key="reg_user")
            password = st.text_input("密碼", type="password", key="reg_pass")
            password2 = st.text_input("確認密碼", type="password", key="reg_pass2")
            
            if st.form_submit_button("註冊", use_container_width=True):
                if not st.session_state.supabase_client:
                    st.error("請先在左側設定 Supabase 連接")
                elif not username or not password:
                    st.warning("請輸入使用者名稱和密碼")
                elif password != password2:
                    st.error("兩次密碼輸入不一致")
                elif len(password) < 6:
                    st.warning("密碼至少需要 6 個字元")
                else:
                    try:
                        # 檢查使用者名稱是否已存在
                        existing = st.session_state.supabase_client.client.table("users")\
                            .select("id")\
                            .eq("username", username)\
                            .execute()
                        
                        if existing.data:
                            st.error("使用者名稱已存在")
                        else:
                            result = st.session_state.supabase_client.client.table("users")\
                                .insert({"username": username, "password": password})\
                                .execute()
                            st.success("註冊成功! 請登入 ✅")
                    except Exception as e:
                        st.error(f"註冊失敗: {str(e)}")

def main():
    """主程式"""
    init_session_state()
    render_sidebar()
    
    st.title("🌟 個人穿搭 AI 助手")
    
    # 檢查是否已登入
    if not st.session_state.user_id:
        render_login()
        return
    
    # 渲染天氣小工具
    config = st.session_state.config
    if config.weather_api_key and st.session_state.supabase_client:
        weather_service = WeatherService(config.weather_api_key)
        render_weather_widget(weather_service, st.session_state.selected_city)
    
    # 主要內容區域
    tab1, tab2, tab3 = st.tabs(["📸 上傳入庫", "👔 我的衣櫥", "💡 今日推薦"])
    
    # 初始化服務
    ai_service = AIService(config.gemini_api_key, config.api_rate_limit_seconds)
    wardrobe_service = WardrobeService(st.session_state.supabase_client)
    weather_service = WeatherService(config.weather_api_key)
    
    with tab1:
        render_upload_page(ai_service, wardrobe_service, config)
    
    with tab2:
        render_wardrobe_page(wardrobe_service, st.session_state.user_id)
    
    with tab3:
        render_recommendation_page(
            ai_service,
            wardrobe_service,
            weather_service,
            st.session_state.user_id,
            st.session_state.selected_city
        )

if __name__ == "__main__":
    main()
