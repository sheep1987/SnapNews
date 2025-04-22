"""
新闻API相关工具函数
"""
import os
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

# 加载环境变量
load_dotenv()

# 获取API密钥
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", "40"))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "zh")


def fetch_news(tags, language=DEFAULT_LANGUAGE, max_items=MAX_NEWS_ITEMS):
    """
    根据标签获取新闻
    
    参数:
        tags (list): 标签列表
        language (str): 新闻语言
        max_items (int): 最大新闻条数
    
    返回:
        pandas.DataFrame: 新闻数据框
    """
    # 构建查询字符串
    query = " OR ".join(tags)
    
    # 计算30天前的日期作为开始日期
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    # 使用今天的日期作为结束日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # NewsAPI请求参数
    params = {
        'q': query,
        'apiKey': NEWS_API_KEY,
        'language': language,
        'from': month_ago,
        'to': today,
        'sortBy': 'publishedAt',
        'pageSize': max_items
    }
    
    try:
        # 发送请求前打印使用的API密钥（仅用于调试，生产环境应删除）
        print(f"使用的API密钥: {NEWS_API_KEY[:5]}...{NEWS_API_KEY[-5:]}")
        
        # 发送请求
        response = requests.get('https://newsapi.org/v2/everything', params=params)
        response.raise_for_status()
        
        # 解析响应
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            return pd.DataFrame()
        
        # 创建数据框
        df = pd.DataFrame(articles)
        
        # 处理日期
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df = df.sort_values('publishedAt', ascending=False)
        
        # 提取需要的字段
        if 'source' in df.columns:
            df['source'] = df['source'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else '')
        
        return df
    
    except Exception as e:
        print(f"获取新闻时出错: {e}")
        # 添加更详细的错误信息
        if isinstance(e, requests.exceptions.HTTPError):
            print(f"HTTP状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
        return pd.DataFrame()


def get_top_news(news_df, top_n=8):
    """
    获取前N条新闻
    
    参数:
        news_df (pandas.DataFrame): 新闻数据框
        top_n (int): 返回的新闻条数
    
    返回:
        pandas.DataFrame: 前N条新闻
    """
    if news_df.empty:
        return news_df
    
    return news_df.head(top_n) 