"""
衣櫥頁面組件 - 優化版
處理衣櫥管理的 UI 邏輯,包含批量刪除即時刷新
"""
import streamlit as st
import base64
import io
from PIL import Image
from api.wardrobe_service import WardrobeService

def render_wardrobe_page(wardrobe_service: WardrobeService, user_id: str):
    """
    渲染衣櫥頁面
    
    Args:
        wardrobe_service: 衣櫥服務實例
        user_id: 使用者 ID
    """
    st.header("我的雲端衣櫥")
    
    # 初始化批量刪除模式狀態
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
        if st.button(
            "🗑️ 批量刪除" if not st.session_state.batch_delete_mode else "✅ 完成", 
            use_container_width=True,
            type="secondary" if not st.session_state.batch_delete_mode else "primary"
        ):
            st.session_state.batch_delete_mode = not st.session_state.batch_delete_mode
            if not st.session_state.batch_delete_mode:
                st.session_state.selected_items = []
            st.rerun()
    
    # 讀取衣櫥資料
    items = wardrobe_service.get_wardrobe(user_id)
    
    if not items:
        st.info("衣櫥是空的,去上傳一些衣服吧! 👕")
        return
    
    # 顯示統計
    st.write(f"共有 **{len(items)}** 件衣服")
    
    # 分類統計
    categories = wardrobe_service.get_category_statistics(user_id)
    if categories:
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        for i, (cat, count) in enumerate(categories.items()):
            with cols[i % 4]:
                st.metric(cat, count)
    
    st.divider()
    
    # 批量刪除模式提示和操作
    if st.session_state.batch_delete_mode:
        st.warning("🗑️ 批量刪除模式:勾選要刪除的衣服")
        
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
                    # 執行批量刪除
                    with st.spinner("刪除中..."):
                        success, success_count, fail_count = wardrobe_service.batch_delete_items(
                            user_id, 
                            st.session_state.selected_items
                        )
                    
                    # 顯示結果
                    if success:
                        st.success(f"✅ 已刪除 {success_count} 件衣服")
                        if fail_count > 0:
                            st.warning(f"⚠️ {fail_count} 件刪除失敗")
                    else:
                        st.error("❌ 批量刪除失敗")
                    
                    # 清空選擇並退出批量模式
                    st.session_state.selected_items = []
                    st.session_state.batch_delete_mode = False
                    
                    # 🔥 關鍵:立即刷新頁面
                    st.rerun()
        
        st.divider()
    
    # 顯示衣物卡片
    _render_wardrobe_grid(items, wardrobe_service, user_id)


def _render_wardrobe_grid(items, wardrobe_service: WardrobeService, user_id: str):
    """
    渲染衣櫥網格
    
    Args:
        items: 衣物列表
        wardrobe_service: 衣櫥服務
        user_id: 使用者 ID
    """
    cols = st.columns(3)
    
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                # 批量刪除模式:顯示選擇框
                if st.session_state.batch_delete_mode:
                    is_selected = item.id in st.session_state.selected_items
                    if st.checkbox(
                        "選擇", 
                        value=is_selected, 
                        key=f"check_{item.id}"
                    ):
                        if item.id not in st.session_state.selected_items:
                            st.session_state.selected_items.append(item.id)
                    else:
                        if item.id in st.session_state.selected_items:
                            st.session_state.selected_items.remove(item.id)
                
                # 顯示圖片
                if item.image_data:
                    try:
                        img_bytes = base64.b64decode(item.image_data)
                        img = Image.open(io.BytesIO(img_bytes))
                        st.image(img, use_container_width=True)
                    except:
                        st.write("🖼️ 圖片載入失敗")
                
                # 顯示資訊
                st.subheader(item.name)
                st.write(f"**類別:** {item.category}")
                st.write(f"**顏色:** {item.color}")
                st.write(f"**風格:** {item.style}")
                st.write(f"**保暖度:** {'🔥' * item.warmth}")
                
                # 單件刪除按鈕(非批量模式時顯示)
                if not st.session_state.batch_delete_mode:
                    if st.button("🗑️ 刪除", key=f"del_{item.id}", use_container_width=True):
                        if wardrobe_service.delete_item(user_id, item.id):
                            st.success("✅ 已刪除")
                            st.rerun()
                        else:
                            st.error("❌ 刪除失敗")
