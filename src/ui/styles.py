"""
CSS 樣式定義 - 修正版
使用純 CSS 實現可點擊的回到頂端按鈕
"""
import streamlit as st
import streamlit.components.v1 as components

def apply_custom_styles():
    """
    應用自定義 CSS 樣式
    包含響應式設計和移動端優化
    """
    st.markdown("""
    <style>
    /* ========== 隱藏頂部圖標 ========== */
    header[data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }
    
    /* 修正頂部空白 */
    .block-container {
        padding-top: 2rem;
    }
    
    /* ========== 卡片樣式優化 ========== */
    [data-testid="stVerticalBlock"] > div:has(> div[data-testid="stContainer"]) {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* ========== 響應式網格 ========== */
    @media (max-width: 768px) {
        /* 手機版單列顯示 */
        .stColumn {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        
        /* 增大點擊區域 */
        button {
            min-height: 44px;
            font-size: 16px;
        }
        
        /* 優化輸入框 */
        input, textarea, select {
            font-size: 16px;
            min-height: 44px;
        }
        
        /* 優化圖片顯示 */
        img {
            max-width: 100%;
            height: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_scroll_to_top_button():
    """
    渲染回到頂端按鈕
    使用 Streamlit Components 實現 JavaScript 功能
    """
    # 使用 components.html 嵌入可執行的 JavaScript
    components.html(
        """
        <style>
        .scroll-to-top-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-size: 24px;
            transition: all 0.3s ease;
            display: none;
            align-items: center;
            justify-content: center;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        
        .scroll-to-top-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .scroll-to-top-btn:active {
            transform: translateY(-2px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        }
        
        .scroll-to-top-btn.show {
            display: flex;
        }
        
        /* 手機版優化 */
        @media (max-width: 768px) {
            .scroll-to-top-btn {
                width: 50px;
                height: 50px;
                font-size: 20px;
                bottom: 15px;
                right: 15px;
            }
        }
        </style>
        
        <button class="scroll-to-top-btn" id="scrollTopBtn" title="回到頂端">
            ⬆️
        </button>
        
        <script>
        (function() {
            const btn = document.getElementById('scrollTopBtn');
            
            // 點擊按鈕回到頂端
            btn.addEventListener('click', function() {
                // 獲取父窗口（Streamlit 主窗口）
                window.parent.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                
                // 觸覺反饋（支援的設備）
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            });
            
            // 監聽父窗口的滾動事件
            function checkScroll() {
                const scrollY = window.parent.scrollY || window.parent.pageYOffset;
                
                if (scrollY > 300) {
                    btn.classList.add('show');
                } else {
                    btn.classList.remove('show');
                }
            }
            
            // 定期檢查滾動位置（因為無法直接監聽父窗口事件）
            setInterval(checkScroll, 100);
            
            // 初始檢查
            checkScroll();
        })();
        </script>
        """,
        height=0,  # 不佔用額外空間
    )


def apply_mobile_optimizations():
    """
    應用手機版專屬優化
    """
    st.markdown("""
    <style>
    /* 手機版特殊優化 */
    @media (max-width: 768px) {
        /* 優化 metric 顯示 */
        [data-testid="stMetric"] {
            padding: 0.5rem;
        }
        
        /* 優化按鈕間距 */
        .stButton > button {
            margin-bottom: 0.5rem;
        }
        
        /* 優化圖片容器 */
        [data-testid="stImage"] {
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
