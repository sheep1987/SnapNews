"""
SnapNews - 个性化新闻聚合应用主入口
"""
import streamlit as st
from components.sidebar import render_sidebar
from components.news_card import render_news_cards
from components.summary import render_summary_container, stream_summary, render_empty_summary
from utils.news_api import fetch_news, get_top_news
from utils.openai_api import generate_news_summary, DEFAULT_MODEL
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="SnapNews - 个性化新闻聚合",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: #1E88E5;
    }
    
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """
    主函数
    """
    # 渲染侧边栏并获取选中的标签
    selected_tags = render_sidebar()
    
    # 主内容区
    st.title("📰 SnapNews")
    st.write("选择感兴趣的标签，获取个性化新闻推荐和AI摘要")
    
    # 显示已选标签
    if selected_tags:
        st.write("已选标签:")
        cols = st.columns(min(8, len(selected_tags) + 1))
        for i, tag in enumerate(selected_tags):
            with cols[i]:
                st.markdown(f"<div style='background-color: #E3F2FD; padding: 8px; border-radius: 5px; text-align: center;'>{tag}</div>", unsafe_allow_html=True)
    else:
        st.info("请从侧边栏选择感兴趣的标签")
    
    # 初始化状态
    if 'news_data' not in st.session_state:
        st.session_state.news_data = None
    if 'news_summary' not in st.session_state:
        st.session_state.news_summary = None
    
    # 获取新闻按钮
    if st.button("获取新闻", disabled=not selected_tags, type="primary"):
        with st.spinner("正在获取最新新闻..."):
            # 获取新闻数据
            news_df = fetch_news(selected_tags)
            
            if news_df.empty:
                st.error("未能获取到相关新闻，请尝试其他标签或检查API连接")
            else:
                # 获取Top 8新闻
                top_news = get_top_news(news_df)
                st.session_state.news_data = top_news.to_dict('records')
                
                # 所有新闻数据(最多40条)用于AI摘要
                all_news = news_df.head(40).to_dict('records')
                
                # 使用配置的模型，不需要用户选择
                model_to_use = st.session_state.get('selected_model', DEFAULT_MODEL)
                
                # 生成AI摘要
                with st.spinner("正在生成新闻摘要..."):
                    try:
                        st.session_state.news_summary = generate_news_summary(all_news, selected_tags, model=model_to_use)
                    except Exception as e:
                        st.error(f"摘要生成失败：{str(e)}")
                        # 如果是地区限制错误，自动尝试回退到OpenAI模型
                        if "unsupported_country_region_territory" in str(e) and "deepseek" in model_to_use.lower():
                            st.warning("正在尝试使用备用模型...")
                            try:
                                # 尝试使用OpenAI的模型
                                fallback_model = "gpt-3.5-turbo"
                                st.session_state.news_summary = generate_news_summary(all_news, selected_tags, model=fallback_model)
                            except Exception as fallback_error:
                                st.error(f"备用模型也失败：{str(fallback_error)}")
    
    # 显示新闻和摘要
    if st.session_state.news_data:
        # 创建两列布局
        col1, col2 = st.columns([6, 4])
        
        with col1:
            st.subheader("📱 热门新闻")
            render_news_cards(st.session_state.news_data)
        
        with col2:
            summary_placeholder = render_summary_container()
            # 如果有摘要数据，则流式显示
            if st.session_state.news_summary:
                stream_summary(summary_placeholder, st.session_state.news_summary)
    else:
        # 显示空提示
        st.subheader("📱 热门新闻")
        st.info("选择标签并点击「获取新闻」按钮查看最新新闻")
        
        render_empty_summary()


if __name__ == "__main__":
    main() 