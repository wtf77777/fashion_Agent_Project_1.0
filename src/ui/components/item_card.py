"""
衣物卡片組件
顯示單件衣物的資訊卡片
"""
import streamlit as st
import base64
import io
from PIL import Image
from database.models import ClothingItem

def render_item_card(
    item: ClothingItem, 
    show_delete: bool = True,
    show_checkbox: bool = False,
    is_selected: bool = False,
    on_delete=None,
    on_select=None
):
    """
    渲染衣物卡片
    
    Args:
        item: 衣物資料模型
        show_delete: 是否顯示刪除按鈕
        show_checkbox: 是否顯示選擇框
        is_selected: 是否已選中
        on_delete: 刪除回調函數
        on_select: 選擇回調函數
    """
    with st.container(border=True):
        # 選擇框
        if show_checkbox:
            selected = st.checkbox(
                "選擇", 
                value=is_selected, 
                key=f"check_{item.id}"
            )
            if on_select:
                on_select(item.id, selected)
        
        # 顯示圖片
        if item.image_data:
            try:
                img_bytes = base64.b64decode(item.image_data)
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, use_container_width=True)
            except Exception as e:
                st.error("📷 圖片載入失敗")
        
        # 衣物資訊
        st.subheader(item.name or "未命名")
        
        # 使用兩欄佈局顯示資訊
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**類別**: {item.category or 'N/A'}")
            st.write(f"**顏色**: {item.color or 'N/A'}")
        
        with col2:
            st.write(f"**風格**: {item.style or 'N/A'}")
            # 保暖度視覺化
            warmth_display = "🔥" * (item.warmth or 0)
            st.write(f"**保暖度**: {warmth_display}")
        
        # 刪除按鈕
        if show_delete and not show_checkbox:
            if st.button("🗑️ 刪除", key=f"del_{item.id}", use_container_width=True):
                if on_delete:
                    on_delete(item.id)

def render_item_grid(items: list, columns: int = 3, **card_props):
    """
    以網格形式渲染多個衣物卡片
    
    Args:
        items: 衣物列表
        columns: 欄數
        **card_props: 傳遞給 render_item_card 的其他參數
    """
    if not items:
        st.info("📦 目前沒有衣物")
        return
    
    cols = st.columns(columns)
    
    for idx, item in enumerate(items):
        with cols[idx % columns]:
            render_item_card(item, **card_props)
