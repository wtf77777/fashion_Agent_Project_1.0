"""
衣櫥管理頁面
顯示和管理使用者的所有衣物
"""
import streamlit as st
import time
from api.wardrobe_service import WardrobeService
from ui.components.item_card import render_item_card

def render_wardrobe_page(wardrobe_service: WardrobeService, user_id: str):
    """
    渲染衣櫥管理頁面
    
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
    
    # 頂部操作列
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔄 重新整理", use_container_width=True):
            st.rerun()
    
    with col2:
        button_label = "🗑️ 批次刪除" if not st.session_state.batch_delete_mode else "✅ 完成"
        button_type = "secondary" if not st.session_state.batch_delete_mode else "primary"
        
        if st.button(button_label, use_container_width=True, type=button_type):
            st.session_state.batch_delete_mode = not st.session_state.batch_delete_mode
            if not st.session_state.batch_delete_mode:
                st.session_state.selected_items = []
            st.rerun()
    
    # 獲取衣櫥資料
    items = wardrobe_service.get_wardrobe(user_id)
    
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
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("☑️ 全選", use_container_width=True):
                st.session_state.selected_items = [item.id for item in items]
                st.rerun()
        
        with col2:
            if st.button("⬜ 取消", use_container_width=True):
                st.session_state.selected_items = []
                st.rerun()
        
        with col3:
            if st.session_state.selected_items:
                if st.button(
                    f"🗑️ 刪除選中的 {len(st.session_state.selected_items)} 件", 
                    type="primary", 
                    use_container_width=True
                ):
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
                        time.sleep(1)
                        st.rerun()
        
        st.divider()
    
    # 顯示衣物卡片
    cols = st.columns(3)
    
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            if st.session_state.batch_delete_mode:
                # 批次刪除模式:顯示選擇框
                is_selected = item.id in st.session_state.selected_items
                
                def on_select(item_id, selected):
                    if selected and item_id not in st.session_state.selected_items:
                        st.session_state.selected_items.append(item_id)
                    elif not selected and item_id in st.session_state.selected_items:
                        st.session_state.selected_items.remove(item_id)
                
                render_item_card(
                    item,
                    show_delete=False,
                    show_checkbox=True,
                    is_selected=is_selected,
                    on_select=on_select
                )
            else:
                # 正常模式:顯示刪除按鈕
                def on_delete(item_id):
                    if wardrobe_service.delete_item(user_id, item_id):
                        st.success("已刪除")
                        st.rerun()
                
                render_item_card(
                    item,
                    show_delete=True,
                    on_delete=on_delete
                )
