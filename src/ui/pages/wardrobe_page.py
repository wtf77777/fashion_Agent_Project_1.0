"""
衣櫥管理頁面 - 性能優化版
顯示和管理使用者的所有衣物,減少不必要的重新載入
"""
import streamlit as st
import time
from api.wardrobe_service import WardrobeService
from ui.components.item_card import render_item_card

@st.cache_data(ttl=60, show_spinner=False)  # ✅ 快取 1 分鐘
def get_wardrobe_cached(user_id: str, _service: WardrobeService):
    """
    快取衣櫥資料
    
    Args:
        user_id: 使用者 ID
        _service: 衣櫥服務實例 (前綴 _ 表示不快取此參數)
    """
    return _service.get_wardrobe(user_id)

def render_wardrobe_page(wardrobe_service: WardrobeService, user_id: str):
    """
    渲染衣櫥管理頁面 - 優化版
    
    Args:
        wardrobe_service: 衣櫥服務實例
        user_id: 使用者 ID
    """
    st.header("我的雲端衣櫥")
    
    # 初始化批次刪除模式
    if 'batch_delete_mode' not in st.session_state:
        st.session_state.batch_delete_mode = False
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = []
    
    # ✅ 使用 callback 避免不必要的 rerun
    def toggle_batch_mode():
        st.session_state.batch_delete_mode = not st.session_state.batch_delete_mode
        if not st.session_state.batch_delete_mode:
            st.session_state.selected_items = []
    
    def refresh_data():
        # 清除快取
        get_wardrobe_cached.clear()
        st.cache_data.clear()
    
    # 頂部操作列
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.button("🔄 重新整理", use_container_width=True, on_click=refresh_data)
    
    with col2:
        button_label = "🗑️ 批次刪除" if not st.session_state.batch_delete_mode else "✅ 完成"
        button_type = "secondary" if not st.session_state.batch_delete_mode else "primary"
        
        st.button(
            button_label, 
            use_container_width=True, 
            type=button_type,
            on_click=toggle_batch_mode
        )
    
    # ✅ 使用快取獲取衣櫥資料
    items = get_wardrobe_cached(user_id, wardrobe_service)
    
    if not items:
        st.info("👕 衣櫥是空的,去上傳一些衣服吧! ")
        return
    
    # 顯示統計資訊
    st.write(f"共有 **{len(items)}** 件衣服")
    
    # 分類統計
    categories = wardrobe_service.get_category_statistics(user_id)
    
    if categories:
        cols = st.columns(min(len(categories), 4))
        for idx, (cat, count) in enumerate(categories.items()):
            with cols[idx % 4]:
                st.metric(cat, count)
    
    st.divider()
    
    # 批次刪除模式
    if st.session_state.batch_delete_mode:
        st.warning("🗑️ 批次刪除模式:勾選要刪除的衣服")
        
        def select_all():
            st.session_state.selected_items = [item.id for item in items]
        
        def deselect_all():
            st.session_state.selected_items = []
        
        def delete_selected():
            if st.session_state.selected_items:
                success, success_count, fail_count = wardrobe_service.batch_delete_items(
                    user_id, 
                    st.session_state.selected_items
                )
                
                if success:
                    st.success(f"✅ 已刪除 {success_count} 件衣服")
                    if fail_count > 0:
                        st.warning(f"⚠️ {fail_count} 件刪除失敗")
                    
                    st.session_state.selected_items = []
                    st.session_state.batch_delete_mode = False
                    get_wardrobe_cached.clear()  # 清除快取
                    time.sleep(0.5)
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            st.button("☑️ 全選", use_container_width=True, on_click=select_all)
        
        with col2:
            st.button("⬜ 取消", use_container_width=True, on_click=deselect_all)
        
        with col3:
            if st.session_state.selected_items:
                st.button(
                    f"🗑️ 刪除選中的 {len(st.session_state.selected_items)} 件", 
                    type="primary", 
                    use_container_width=True,
                    on_click=delete_selected
                )
        
        st.divider()
    
    # 顯示衣物卡片
    cols = st.columns(3)
    
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            if st.session_state.batch_delete_mode:
                # 批次刪除模式:顯示選擇框
                is_selected = item.id in st.session_state.selected_items
                
                # ✅ 使用 checkbox 的 key 來追蹤狀態
                selected = st.checkbox(
                    "選擇",
                    value=is_selected,
                    key=f"check_{item.id}_{idx}"
                )
                
                # 更新選中狀態
                if selected and item.id not in st.session_state.selected_items:
                    st.session_state.selected_items.append(item.id)
                elif not selected and item.id in st.session_state.selected_items:
                    st.session_state.selected_items.remove(item.id)
                
                # 顯示卡片內容
                with st.container(border=True):
                    if item.image_data:
                        try:
                            import base64, io
                            from PIL import Image
                            img_bytes = base64.b64decode(item.image_data)
                            img = Image.open(io.BytesIO(img_bytes))
                            st.image(img, use_container_width=True)
                        except:
                            st.error("📷 圖片載入失敗")
                    
                    st.subheader(item.name or "未命名")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**類別**: {item.category or 'N/A'}")
                        st.write(f"**顏色**: {item.color or 'N/A'}")
                    with col_b:
                        st.write(f"**風格**: {item.style or 'N/A'}")
                        st.write(f"**保暖度**: {'🔥' * (item.warmth or 0)}")
            else:
                # 正常模式:顯示刪除按鈕
                def delete_single_item(item_id):
                    if wardrobe_service.delete_item(user_id, item_id):
                        st.success("已刪除")
                        get_wardrobe_cached.clear()  # 清除快取
                        time.sleep(0.5)
                
                render_item_card(
                    item,
                    show_delete=True,
                    on_delete=lambda id=item.id: delete_single_item(id)
                )
