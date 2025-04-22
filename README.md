# SnapNews - 个性化新闻聚合应用

SnapNews是一个使用Streamlit开发的个性化新闻聚合应用，它允许用户根据兴趣标签获取最新新闻，并使用AI生成新闻摘要。

## 功能特点

- 根据用户选择的标签获取相关新闻
- 预设和自定义标签支持
- 新闻热点可视化展示
- AI生成的新闻摘要提供重点内容概览
- 流式显示AI摘要内容
- 响应式布局，适合各种屏幕尺寸

## 技术栈

- Python
- Streamlit (Web界面)
- NewsAPI (新闻数据源)
- DeepSeek AI (生成摘要)
- Pandas (数据处理)

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/你的用户名/SnapNews.git
cd SnapNews
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 复制示例环境变量文件
cp .env.example .env
# 编辑.env文件，添加你的API密钥
```

4. 运行应用
```bash
streamlit run app.py
```

## 环境变量设置

在`.env`文件中配置以下变量:

- `OPENAI_API_KEY` - DeepSeek或OpenAI API密钥
- `NEWS_API_KEY` - NewsAPI密钥
- `DEFAULT_MODEL` - 默认AI模型 (默认: deepseek-chat)
- `DEFAULT_LANGUAGE` - 默认新闻语言 (默认: zh)
- `MAX_NEWS_ITEMS` - 获取的最大新闻条数 (默认: 40)
- `TOP_DISPLAY_ITEMS` - 显示的热门新闻条数 (默认: 8)

## 许可证

MIT

## 联系方式

如有任何问题或建议，请通过GitHub issues联系，或发送邮件至：173548585@qq.com 