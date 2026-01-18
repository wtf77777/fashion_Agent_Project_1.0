"""
UI 樣式定義
集中管理所有 CSS 樣式
"""
import streamlit as st

def apply_custom_styles():
    """應用自定義 CSS 樣式"""
    st.markdown("""
        <style>
        /* 隱藏頂部所有圖標 (Share, Star, GitHub 等) */
        header[data-testid="stHeader"] {
            visibility: hidden;
            display: none;
        }
        
        /* 修正頂部空白 */
        .block-container {
            padding-top: 2rem;
        }
        
        /* 回到頂端按鈕 */
        .scroll-to-top {
            position: fixed;
            bottom: 20px;
            left: 20px;
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
        }
        
        .scroll-to-top:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .scroll-to-top:active {
            transform: translateY(-2px);
        }
        
        /* 卡片陰影效果 */
        [data-testid="stVerticalBlock"] > [style*="border"] {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease;
        }
        
        [data-testid="stVerticalBlock"] > [style*="border"]:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        
        /* 按鈕美化 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Metric 卡片美化 */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        /* 輪播指示器 */
        .carousel-indicator {
            text-align: center;
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
            margin: 10px 0;
            padding: 10px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
        }
        
        /* 成功訊息美化 */
        .stSuccess {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 1rem;
            border-radius: 4px;
        }
        
        /* 警告訊息美化 */
        .stWarning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            border-radius: 4px;
        }
        
        /* 錯誤訊息美化 */
        .stError {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            border-radius: 4px;
        }
        
        /* 資訊訊息美化 */
        .stInfo {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 1rem;
            border-radius: 4px;
        }
        </style>
        
        <a href="#" class="scroll-to-top" title="回到頂端">⬆️</a>
        """, unsafe_allow_html=True)
