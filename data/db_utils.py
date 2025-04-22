"""
数据库工具函数
"""
import sqlite3
import os
import json
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'snapnews.db')


def initialize_db():
    """
    初始化数据库
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建标签表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建用户标签表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建收藏的新闻表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT UNIQUE,
        source TEXT,
        description TEXT,
        published_at TIMESTAMP,
        image_url TEXT,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建标签组合表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tag_combinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()


def save_news(news_item):
    """
    保存新闻到收藏
    
    参数:
        news_item: 新闻项数据
    
    返回:
        bool: 是否保存成功
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_news'")
        if not cursor.fetchone():
            initialize_db()
        
        # 插入数据
        cursor.execute('''
        INSERT OR IGNORE INTO saved_news (title, url, source, description, published_at, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            news_item.get('title'),
            news_item.get('url'),
            news_item.get('source'),
            news_item.get('description'),
            news_item.get('publishedAt'),
            news_item.get('urlToImage')
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    except Exception as e:
        print(f"保存新闻时出错: {e}")
        return False


def get_saved_news():
    """
    获取所有已收藏的新闻
    
    返回:
        list: 收藏的新闻列表
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_news'")
        if not cursor.fetchone():
            initialize_db()
            return []
        
        # 查询数据
        cursor.execute('''
        SELECT * FROM saved_news ORDER BY saved_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        result = []
        for row in rows:
            item = dict(row)
            # 重命名字段以匹配API格式
            item['publishedAt'] = item.pop('published_at')
            item['urlToImage'] = item.pop('image_url')
            result.append(item)
        
        return result
    
    except Exception as e:
        print(f"获取收藏新闻时出错: {e}")
        return []


def save_tag_combination(name, tags):
    """
    保存标签组合
    
    参数:
        name: 组合名称
        tags: 标签列表
    
    返回:
        bool: 是否保存成功
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag_combinations'")
        if not cursor.fetchone():
            initialize_db()
        
        # 插入数据
        cursor.execute('''
        INSERT OR REPLACE INTO tag_combinations (name, tags, created_at)
        VALUES (?, ?, ?)
        ''', (
            name,
            json.dumps(tags),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    except Exception as e:
        print(f"保存标签组合时出错: {e}")
        return False


def get_tag_combinations():
    """
    获取所有标签组合
    
    返回:
        dict: 标签组合字典，键为名称，值为标签列表
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag_combinations'")
        if not cursor.fetchone():
            initialize_db()
            return {}
        
        # 查询数据
        cursor.execute('''
        SELECT name, tags FROM tag_combinations ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典
        result = {}
        for row in rows:
            result[row['name']] = json.loads(row['tags'])
        
        return result
    
    except Exception as e:
        print(f"获取标签组合时出错: {e}")
        return {} 