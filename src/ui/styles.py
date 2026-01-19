"""
CSS 樣式定義 - 手機優化版
包含移動端兼容的回到頂端按鈕
"""
import streamlit as st

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
    
    /* ========== 回到頂端按鈕 ========== */
    .scroll-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;  /* 改為右下角,避免遮擋內容 */
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
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        /* 🔥 關鍵:使用 JavaScript 而非錨點 */
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }
    
    .scroll-to-top:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .scroll-to-top:active {
        transform: translateY(-2px);
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
    }
    
    /* ========== 手機版優化 ========== */
    @media (max-width: 768px) {
        .scroll-to-top {
            width: 50px;
            height: 50px;
            font-size: 20px;
            bottom: 15px;
            right: 15px;
        }
        
        /* 優化手機版觸控區域 */
        .scroll-to-top::before {
            content: '';
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
        }
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
    }
    </style>
    
    <!-- 🔥 使用 JavaScript 實現平滑滾動 -->
    <script>
    // 等待 DOM 載入完成
    document.addEventListener('DOMContentLoaded', function() {
        // 創建回到頂端按鈕
        createScrollButton();
        
        // 監聽滾動事件,顯示/隱藏按鈕
        window.addEventListener('scroll', toggleScrollButton);
    });
    
    function createScrollButton() {
        // 檢查按鈕是否已存在
        if (document.getElementById('scroll-top-btn')) return;
        
        // 創建按鈕元素
        const btn = document.createElement('button');
        btn.id = 'scroll-top-btn';
        btn.className = 'scroll-to-top';
        btn.innerHTML = '⬆️';
        btn.title = '回到頂端';
        btn.style.display = 'none';
        
        // 添加點擊事件
        btn.addEventListener('click', scrollToTop);
        
        // 添加到頁面
        document.body.appendChild(btn);
    }
    
    function scrollToTop(e) {
        e.preventDefault();
        
        // 平滑滾動到頂部
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        
        // 添加觸覺反饋(支援的設備)
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
    }
    
    function toggleScrollButton() {
        const btn = document.getElementById('scroll-top-btn');
        if (!btn) return;
        
        // 滾動超過 300px 時顯示按鈕
        if (window.scrollY > 300) {
            btn.style.display = 'flex';
        } else {
            btn.style.display = 'none';
        }
    }
    
    // Streamlit 特殊處理:監聽頁面重新渲染
    const observer = new MutationObserver(function() {
        createScrollButton();
        toggleScrollButton();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
    """, unsafe_allow_html=True)


def apply_mobile_optimizations():
    """
    應用手機版專屬優化
    """
    st.markdown("""
    <style>
    /* 手機版特殊優化 */
    @media (max-width: 768px) {
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
        
        /* 優化 metric 顯示 */
        [data-testid="stMetric"] {
            padding: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
