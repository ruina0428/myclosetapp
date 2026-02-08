import streamlit as st
import os
from PIL import Image
import uuid

# ---------------------- 页面配置（适配移动端） ----------------------
st.set_page_config(
    page_title="我的衣橱（手机版）",
    page_icon="👗",
    layout="centered",  # 移动端用centered更友好
    initial_sidebar_state="collapsed"  # 收起侧边栏，节省手机空间
)

# ---------------------- 隐藏默认样式 + 移动端适配CSS ----------------------
custom_css = """
<style>
/* 隐藏默认菜单和页脚 */
#MainMenu, footer {visibility: hidden;}

/* 适配手机的按钮/卡片样式 */
.stButton>button {
    width: 100%;
    font-size: 16px;  /* 手机字体放大 */
    padding: 10px 0;
}
.stFileUploader {
    padding: 10px 0;
}
/* 悬浮加号按钮（手机端调整位置） */
.floating-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #2196F3;
    color: white;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    z-index: 1000;
}
/* 图片卡片间距 */
div[data-testid="column"] {
    padding: 5px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------- 初始化文件夹（保存上传的照片） ----------------------
# 自动创建分类文件夹，不用手动建
categories = ["上装", "下装", "鞋子", "包包", "配饰"]
for cate in categories:
    if not os.path.exists(cate):
        os.makedirs(cate)

# ---------------------- 悬浮加号按钮（唤起上传弹窗） ----------------------
st.markdown('<div class="floating-btn" onclick="document.getElementById(\'upload-btn\').click()">+</div>', unsafe_allow_html=True)

# ---------------------- 照片上传功能（手机端核心） ----------------------
# ---------------------- 照片上传功能（修复重复上传问题） ----------------------
with st.expander("📸 上传新衣物（手机点这里选相册）", expanded=False):
    # 1. 选择分类
    selected_cate = st.selectbox("选择衣物分类", categories, key="upload-cate")
    # 2. 文件上传组件（支持手机相册，accept限制只选图片）
    uploaded_file = st.file_uploader(
        "从手机相册选择照片",
        type=["jpg", "jpeg", "png"],
        key="upload-btn",
        label_visibility="collapsed"
    )
    # 3. 保存上传的照片（添加防重复逻辑）
    if uploaded_file is not None:
        # 生成唯一文件名，用图片的哈希值来避免重复
        import hashlib
        file_hash = hashlib.md5(uploaded_file.getbuffer()).hexdigest()
        file_name = f"{file_hash}.{uploaded_file.name.split('.')[-1]}"
        file_path = os.path.join(selected_cate, file_name)
        
        # 只有当文件不存在时才保存
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ {selected_cate}上传成功！")
        else:
            st.info(f"ℹ️ 该图片已存在，无需重复上传")
        # 不再用st.rerun，改用Streamlit的状态管理刷新
        st.session_state["upload_trigger"] = not st.session_state.get("upload_trigger", False)

# ---------------------- 按分类展示衣物（手机端横向滚动） ----------------------
st.title("👗 我的衣橱")
for cate in categories:
    # 获取该分类下的所有图片
    img_files = [f for f in os.listdir(cate) if f.endswith(("jpg", "jpeg", "png"))]
    # 显示分类标题+数量
    st.subheader(f"{cate} · {len(img_files)}个")
    
    if len(img_files) > 0:
        # 手机端横向排列图片（自动适配数量）
        cols = st.columns(min(len(img_files), 4))  # 最多一行4张，适配手机
        for idx, img_file in enumerate(img_files):
            with cols[idx % len(cols)]:
                # 显示图片
                img_path = os.path.join(cate, img_file)
                st.image(img_path, use_column_width=True)
                # 可选：添加删除按钮
                if st.button("🗑️ 删除", key=f"del-{cate}-{img_file}"):
                    os.remove(img_path)
                    st.success(f"已删除{cate}：{img_file}")
                    st.rerun()
    else:
        # 空分类提示
        st.write("暂无衣物，点击上方「上传新衣物」添加～")

    st.divider()  # 分类之间加分隔线，手机上更清晰
