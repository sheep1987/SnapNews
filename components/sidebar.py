"""
侧边栏组件
"""
import streamlit as st
import os
from config.default_tags import DEFAULT_TAGS, HOT_TAGS, TECH_TAGS, BUSINESS_TAGS, SCIENCE_TAGS
from utils.openai_api import MODEL_PROVIDERS

# 获取默认模型
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")

def initialize_session_state():
    """初始化会话状态"""
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    if 'custom_tags' not in st.session_state:
        st.session_state.custom_tags = []
    
    if 'tag_combinations' not in st.session_state:
        st.session_state.tag_combinations = {}
    
    # 设置默认模型（不在UI中显示，但在后端使用）
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL


def add_custom_tag():
    """添加自定义标签"""
    new_tag = st.session_state.new_custom_tag.strip()
    if new_tag and new_tag not in st.session_state.custom_tags and new_tag not in DEFAULT_TAGS:
        st.session_state.custom_tags.append(new_tag)
        st.session_state.new_custom_tag = ""


def save_tag_combination():
    """保存标签组合"""
    name = st.session_state.combination_name.strip()
    if name and st.session_state.selected_tags:
        st.session_state.tag_combinations[name] = st.session_state.selected_tags.copy()
        st.session_state.combination_name = ""


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("SnapNews")
        st.markdown("---")
        
        # 初始化会话状态
        initialize_session_state()
        
        # 选项卡
        tab1, tab2, tab3 = st.tabs(["预设标签", "自定义标签", "标签组合"])
        
        # 预设标签选项卡
        with tab1:
            st.subheader("热门标签")
            for tag in HOT_TAGS:
                if st.checkbox(tag, value=tag in st.session_state.selected_tags, key=f"hot_{tag}"):
                    if tag not in st.session_state.selected_tags:
                        st.session_state.selected_tags.append(tag)
                else:
                    if tag in st.session_state.selected_tags:
                        st.session_state.selected_tags.remove(tag)
            
            # 技术标签
            with st.expander("技术标签", expanded=False):
                for tag in TECH_TAGS:
                    if tag not in HOT_TAGS:  # 避免重复
                        if st.checkbox(tag, value=tag in st.session_state.selected_tags, key=f"tech_{tag}"):
                            if tag not in st.session_state.selected_tags:
                                st.session_state.selected_tags.append(tag)
                        else:
                            if tag in st.session_state.selected_tags:
                                st.session_state.selected_tags.remove(tag)
            
            # 商业标签
            with st.expander("商业标签", expanded=False):
                for tag in BUSINESS_TAGS:
                    if tag not in HOT_TAGS:  # 避免重复
                        if st.checkbox(tag, value=tag in st.session_state.selected_tags, key=f"biz_{tag}"):
                            if tag not in st.session_state.selected_tags:
                                st.session_state.selected_tags.append(tag)
                        else:
                            if tag in st.session_state.selected_tags:
                                st.session_state.selected_tags.remove(tag)
            
            # 科学标签
            with st.expander("科学标签", expanded=False):
                for tag in SCIENCE_TAGS:
                    if tag not in HOT_TAGS:  # 避免重复
                        if st.checkbox(tag, value=tag in st.session_state.selected_tags, key=f"sci_{tag}"):
                            if tag not in st.session_state.selected_tags:
                                st.session_state.selected_tags.append(tag)
                        else:
                            if tag in st.session_state.selected_tags:
                                st.session_state.selected_tags.remove(tag)
        
        # 自定义标签选项卡
        with tab2:
            st.subheader("创建自定义标签")
            st.text_input("输入新标签", key="new_custom_tag")
            st.button("添加标签", on_click=add_custom_tag)
            
            st.subheader("自定义标签列表")
            for tag in st.session_state.custom_tags:
                if st.checkbox(tag, value=tag in st.session_state.selected_tags, key=f"custom_{tag}"):
                    if tag not in st.session_state.selected_tags:
                        st.session_state.selected_tags.append(tag)
                else:
                    if tag in st.session_state.selected_tags:
                        st.session_state.selected_tags.remove(tag)
        
        # 标签组合选项卡
        with tab3:
            st.subheader("保存当前标签组合")
            st.text_input("组合名称", key="combination_name")
            st.button("保存组合", on_click=save_tag_combination)
            
            st.subheader("加载标签组合")
            for name, tags in st.session_state.tag_combinations.items():
                if st.button(name, key=f"load_{name}"):
                    st.session_state.selected_tags = tags.copy()
        
        st.markdown("---")
        st.caption("© 2023 SnapNews")
    
    return st.session_state.selected_tags 