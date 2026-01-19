"""
簡化版 Top 按鈕
使用 HTML 錨點實現，不依賴 JavaScript
"""
import streamlit as st

def render_simple_top_button():
    """
    渲染簡化版回到頂端按鈕
    使用 HTML 錨點，所有瀏覽器都支援
    """
    st.markdown("""
    <style>
    .top-anchor {
        position: absolute;
        top: 0;
        left: 0;
        visibility: hidden;
    }
    
    .scroll-to-top-link {
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
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        -webkit-tap-highlight-color: transparent;
    }
    
    .scroll-to-top-link:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    @media (max-width: 768px) {
        .scroll-to-top-link {
            width: 50px;
            height: 50px;
            font-size: 20px;
            bottom: 15px;
            right: 15px;
        }
    }
    </style>
    
    <div id="top" class="top-anchor"></div>
    <a href="#top" class="scroll-to-top-link" title="回到頂端">⬆️</a>
    """, unsafe_allow_html=True)
