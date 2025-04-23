"""
新闻卡片组件
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import pytz


def format_date(date_str):
    """
    格式化日期
    
    参数:
        date_str: 日期字符串或datetime对象
    
    返回:
        str: 格式化后的日期字符串
    """
    if isinstance(date_str, str):
        date = pd.to_datetime(date_str)
    else:
        # 确保即使传入的是 datetime 对象，也转换为 pandas Timestamp
        date = pd.Timestamp(date_str)

    # 获取当前的 UTC 时间 (timezone-aware)
    now_utc = pd.Timestamp.now(tz='UTC')

    # 检查 date 是否是 timezone-naive
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        # 如果是 naive，假定它是 UTC 时间并使其 aware
        date_utc = date.tz_localize('UTC')
    else:
        # 如果已经是 aware，将其转换为 UTC
        date_utc = date.tz_convert('UTC')

    # 现在 now_utc 和 date_utc 都是 timezone-aware 且在 UTC 时区
    diff = now_utc - date_utc
    
    if diff.days == 0:
        if diff.seconds < 3600:
            return f"{diff.seconds // 60}分钟前"
        else:
            return f"{diff.seconds // 3600}小时前"
    elif diff.days == 1:
        return "昨天"
    else:
        # 格式化时，最好转换为本地时间以获得更友好的显示
        local_date = date_utc.tz_convert(pytz.timezone('Asia/Shanghai')) # 或者你需要的本地时区
        return local_date.strftime("%m月%d日")


def render_news_card(news_item):
    """
    渲染单个新闻卡片
    
    参数:
        news_item: 新闻项数据
    """
    # 提取数据
    title = news_item.get("title", "无标题")
    url = news_item.get("url", "#")
    source = news_item.get("source", "未知来源")
    published_at = news_item.get("publishedAt", datetime.now())
    description = news_item.get("description", "")
    image_url = news_item.get("urlToImage", "")
    
    # 截断过长的描述
    short_desc = description[:120] + "..." if len(description) > 120 else description
    
    # 卡片样式
    card_style = """
    <style>
    .news-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.3s;
    }
    .news-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .news-title {
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 18px;
    }
    .news-meta {
        color: #666;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .news-desc {
        font-size: 14px;
        color: #333;
    }
    .news-img {
        border-radius: 4px;
        max-width: 100%;
    }
    </style>
    """
    
    # 显示卡片
    st.markdown(card_style, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{title}</div>
            <div class="news-meta">{source} · {format_date(published_at)}</div>
            <div class="news-desc">{short_desc}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if image_url:
            st.image(image_url, use_container_width=True)
    
    # 链接按钮
    if st.button("阅读全文", key=f"btn_{hash(title)}"):
        st.markdown(f"<a href='{url}' target='_blank'>在新窗口中打开</a>", unsafe_allow_html=True)


def render_news_cards(news_data):
    """
    渲染新闻卡片列表
    
    参数:
        news_data: 新闻数据列表
    """
    if not news_data or len(news_data) == 0:
        st.warning("没有找到相关新闻")
        return
    
    for news_item in news_data:
        render_news_card(news_item)
        st.markdown("---") 