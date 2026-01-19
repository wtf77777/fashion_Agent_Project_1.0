"""
上傳頁面組件 - 優化版
處理衣物上傳的 UI 邏輯，優化批量上傳體驗
"""
import streamlit as st
import io
from PIL import Image
from typing import List
from api.ai_service import AIService
from api.wardrobe_service import WardrobeService
from database.models import ClothingItem

def render_upload_page(
    ai_service: AIService,
    wardrobe_service: WardrobeService,
    config
):
    """渲染上傳頁面"""
    st.header("上傳新衣到雲端")
    
    # 初始化上傳狀態
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state.uploaded_files_cache = []
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    
    # 文件上傳器
    uploaded_files = st.file_uploader(
        "選取多張衣服照片(建議 5-10 張最佳)...", 
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        # 檢查數量限制
        if len(uploaded_files) > config.max_batch_upload:
            st.error(f"⚠️ 一次最多只能上傳 {config.max_batch_upload} 張照片，您選擇了 {len(uploaded_files)} 張")
            st.info(f"📌 請重新選擇不超過 {config.max_batch_upload} 張照片")
            return
        
        # 過濾掉已處理的文件
        active_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
        
        if not active_files:
            st.info("✅ 所有選擇的圖片都已上傳完成！")
            if st.button("🔄 清空並重新選擇", use_container_width=True):
                st.session_state.processed_files = set()
                st.rerun()
            return
        
        st.success(f"✅ 已選擇 {len(active_files)} 張照片 (共 {len(uploaded_files)} 張)")
        
        if len(uploaded_files) > len(active_files):
            st.info(f"ℹ️ 已自動過濾 {len(uploaded_files) - len(active_files)} 張已上傳的圖片")
        
        
        
        # 🔥 位置 1：顯示已選擇統計和批量上傳按鈕
        st.markdown("---")
        col1, col2 = st.columns([0, 1])
        
        with col1:
            st.metric("📸 待上傳", len(active_files))
        
        with col2:
            # 🔥 關鍵：批量上傳按鈕移到這裡
            if st.button(
                f"🚀 批量辨識並上傳全部 ({len(active_files)} 張)", 
                type="primary", 
                use_container_width=True
            ):
                _handle_batch_upload(
                    active_files,
                    ai_service,
                    wardrobe_service,
                    st.session_state.user_id,
                    config
                )
        # 預覽照片（使用可摺疊區域）
            with st.expander("👀 預覽所有照片", expanded=True):
                _render_image_preview(active_files)
    st.divider()
    st.info("""
    **📌 使用提示:**
    1. 拍攝清晰的單件衣服照片
    2. 背景簡潔有助於 AI 辨識
    3. **🚀 批量上傳模式: 5-10 張最佳** (只需 1 次 API 呼叫)
    4. 系統會自動過濾重複的衣服
    5. 已上傳的圖片會自動從列表移除
    6. 批量模式速度提升 10 倍，避免 RPM 限制
    """)


def _render_image_preview(files):
    """
    渲染圖片預覽網格
    
    Args:
        files: 文件列表
    """
    cols = st.columns(4)
    for idx, file in enumerate(files):
        with cols[idx % 4]:
            try:
                img = Image.open(file)
                st.image(img, caption=file.name, use_container_width=True)
                
                # 顯示文件大小
                file.seek(0, 2)  # 移到文件末尾
                size_kb = file.tell() / 1024
                file.seek(0)  # 重置指針
                st.caption(f"📦 {size_kb:.1f} KB")
            except Exception as e:
                st.error(f"❌ {file.name} 無法預覽")


def _handle_batch_upload(
    uploaded_files,
    ai_service: AIService,
    wardrobe_service: WardrobeService,
    user_id: str,
    config
):
    """
    處理批量上傳邏輯
    
    Args:
        uploaded_files: 上傳的文件列表
        ai_service: AI 服務
        wardrobe_service: 衣櫥服務
        user_id: 使用者 ID
        config: 配置對象
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # === 階段 1: 準備圖片資料 ===
    status_text.text("📦 正在準備圖片資料...")
    img_data_list = []
    img_hash_list = []
    file_names = []
    duplicate_count = 0
    skipped_files = []
    
    for file in uploaded_files:
        try:
            img = Image.open(file)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            img_hash = wardrobe_service.get_image_hash(img_bytes)
            
            # 檢查重複
            is_duplicate, existing_name = wardrobe_service.check_duplicate_image(user_id, img_hash)
            if is_duplicate:
                duplicate_count += 1
                skipped_files.append(file.name)
                st.warning(f"⚠️ {file.name} 重複 (已存在: {existing_name})")
                continue
            
            img_data_list.append(img_bytes)
            img_hash_list.append(img_hash)
            file_names.append(file.name)
        except Exception as e:
            st.error(f"❌ {file.name} 讀取失敗: {str(e)}")
            skipped_files.append(file.name)
    
    if not img_data_list:
        st.warning("所有圖片都已存在或無法讀取，沒有新圖片需要上傳")
        progress_bar.empty()
        status_text.empty()
        return
    
    # === 階段 2: AI 批量辨識 ===
    progress_bar.progress(0.3)
    status_text.text(f"🤖 AI 正在批量分析 {len(img_data_list)} 件衣服...")
    st.info(f"⚡ 批量模式: {len(img_data_list)} 張圖片只需 1 次 API 呼叫 (約 20-40 秒)")
    
    tags_list = ai_service.batch_auto_tag(img_data_list)
    
    if not tags_list:
        st.error("❌ 批量辨識失敗，請重試")
        progress_bar.empty()
        status_text.empty()
        return
    
    st.success(f"✅ AI 辨識完成! 共 {len(tags_list)} 件衣服")
    
    # === 階段 3: 儲存到資料庫 ===
    progress_bar.progress(0.6)
    status_text.text("💾 正在存入資料庫...")
    
    success_count = 0
    fail_count = 0
    successfully_uploaded = []
    
    for idx, (tags, img_bytes, img_hash, file_name) in enumerate(zip(
        tags_list, img_data_list, img_hash_list, file_names
    )):
        progress = 0.6 + 0.4 * (idx + 1) / len(img_data_list)
        progress_bar.progress(progress)
        status_text.text(f"正在存入: {file_name} ({idx + 1}/{len(img_data_list)})")
        
        try:
            item = ClothingItem(
                name=tags['name'],
                category=tags['category'],
                color=tags['color'],
                style=tags.get('style', ''),
                warmth=tags['warmth'],
                user_id=user_id
            )
            
            success, result = wardrobe_service.save_item(item, img_bytes)
            
            if success:
                success_count += 1
                successfully_uploaded.append(file_name)
                st.success(f"✅ {file_name} → {tags['name']}")
            else:
                fail_count += 1
                st.error(f"❌ {file_name} 存入失敗: {result}")
        
        except Exception as e:
            fail_count += 1
            st.error(f"❌ {file_name} 處理失敗: {str(e)}")
    
    progress_bar.progress(1.0)
    status_text.empty()
    
    # === 階段 4: 顯示統計 ===
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 處理數", len(img_data_list))
    with col2:
        st.metric("✅ 成功", success_count)
    with col3:
        st.metric("⚠️ 重複/跳過", duplicate_count + len(skipped_files) - duplicate_count)
    with col4:
        st.metric("❌ 失敗", fail_count)
    
    # 🔥 位置 2：自動清除已上傳的文件
    if successfully_uploaded:
        for file_name in successfully_uploaded:
            st.session_state.processed_files.add(file_name)
        
        st.balloons()
        st.success(f"🎉 批量上傳完成！成功 {success_count} 件")
        st.info("✨ 已上傳的圖片已自動從列表移除")
        
        # 延遲 2 秒後刷新頁面
        import time
        time.sleep(2)
        progress_bar.empty()
        st.rerun()
