"""
上傳頁面組件
處理衣物上傳的 UI 邏輯
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
    
    # 只保留批次上傳模式
    uploaded_files = st.file_uploader(
        "選取多張衣服照片(建議 5-10 張最佳)...", 
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # 檢查數量限制
        if len(uploaded_files) > config.max_batch_upload:
            st.error(f"⚠️ 一次最多只能上傳 {config.max_batch_upload} 張照片,您選擇了 {len(uploaded_files)} 張")
            st.info(f"📌 請重新選擇不超過 {config.max_batch_upload} 張照片")
            return
        
        st.success(f"✅ 已選擇 {len(uploaded_files)} 張照片")
        
        # 預覽照片
        with st.expander("👀 預覽所有照片", expanded=True):
            cols = st.columns(4)
            for idx, file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    img = Image.open(file)
                    st.image(img, caption=file.name, use_container_width=True)
        
        # 批次上傳按鈕
        if st.button("🚀 批次辨識並上傳全部", type="primary", use_container_width=True):
            _handle_batch_upload(
                uploaded_files,
                ai_service,
                wardrobe_service,
                st.session_state.user_id
            )
    
    st.divider()
    st.info("""
    **📌 使用提示:**
    1. 拍攝清晰的單件衣服照片
    2. 背景簡潔有助於 AI 辨識
    3. **🚀 批次上傳模式: 5-10 張最佳** (只需 1 次 API 呼叫)
    4. 系統會自動過濾重複的衣服
    5. 批次模式速度提升 10 倍,避免 RPM 限制
    """)

def _handle_batch_upload(
    uploaded_files,
    ai_service: AIService,
    wardrobe_service: WardrobeService,
    user_id: str
):
    """處理批次上傳邏輯"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 準備圖片資料
    status_text.text("📦 正在準備圖片資料...")
    img_data_list = []
    img_hash_list = []
    file_names = []
    duplicate_count = 0
    
    for file in uploaded_files:
        img = Image.open(file)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        img_hash = wardrobe_service.get_image_hash(img_bytes)
        
        # 檢查重複
        is_duplicate, existing_name = wardrobe_service.check_duplicate_image(user_id, img_hash)
        if is_duplicate:
            duplicate_count += 1
            st.warning(f"⚠️ {file.name} 重複 (已存在: {existing_name})")
            continue
        
        img_data_list.append(img_bytes)
        img_hash_list.append(img_hash)
        file_names.append(file.name)
    
    if not img_data_list:
        st.warning("所有圖片都已存在,沒有新圖片需要上傳")
        return
    
    # AI 批次辨識
    progress_bar.progress(0.3)
    status_text.text(f"🤖 AI 正在批次分析 {len(img_data_list)} 件衣服...")
    st.info(f"⚡ 批次模式: {len(img_data_list)} 張圖片只需 1 次 API 呼叫(約 20-40 秒)")
    
    tags_list = ai_service.batch_auto_tag(img_data_list)
    
    if not tags_list:
        st.error("❌ 批次辨識失敗,請重試")
        return
    
    st.success(f"✅ AI 辨識完成! 共 {len(tags_list)} 件衣服")
    
    # 儲存到資料庫
    progress_bar.progress(0.6)
    status_text.text("💾 正在存入資料庫...")
    
    success_count = 0
    fail_count = 0
    
    for idx, (tags, img_bytes, img_hash, file_name) in enumerate(zip(tags_list, img_data_list, img_hash_list, file_names)):
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
                st.success(f"✅ {file_name} → {tags['name']}")
            else:
                fail_count += 1
                st.error(f"❌ {file_name} 存入失敗: {result}")
        
        except Exception as e:
            fail_count += 1
            st.error(f"❌ {file_name} 處理失敗: {str(e)}")
    
    progress_bar.progress(1.0)
    status_text.empty()
    
    # 顯示統計
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 處理數", len(img_data_list))
    with col2:
        st.metric("✅ 成功", success_count)
    with col3:
        st.metric("⚠️ 重複", duplicate_count)
    with col4:
        st.metric("❌ 失敗", fail_count)
    
    if success_count > 0:
        st.balloons()
        st.success(f"🎉 批次上傳完成!成功 {success_count} 件")
