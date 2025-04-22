"""
AI模型API相关工具函数（支持OpenAI和DeepSeek等兼容OpenAI协议的模型）
"""
import os
import openai
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('openai_api')

# 加载环境变量
load_dotenv()

# 获取API密钥和默认模型
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")

# 模型提供商配置
MODEL_PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "api_key_env": "OPENAI_API_KEY"
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
        "api_key_env": "OPENAI_API_KEY"  # 使用与OpenAI相同的环境变量
    },
    # 在此添加其他兼容OpenAI协议的模型提供商
}

# 备用模型设置（当首选模型失败时）
FALLBACK_MODELS = {
    "deepseek-chat": "gpt-3.5-turbo",
    "deepseek-coder": "gpt-3.5-turbo",
    "deepseek-reasoner": "gpt-3.5-turbo"
}

def get_model_provider(model_name):
    """
    根据模型名称确定提供商
    
    参数:
        model_name (str): 模型名称
    
    返回:
        tuple: (provider_name, provider_config)
    """
    for provider, config in MODEL_PROVIDERS.items():
        # 检查模型名称是否包含提供商名称或在提供商的模型列表中
        if provider in model_name.lower() or model_name in config["models"]:
            return provider, config
    
    # 默认返回OpenAI
    return "openai", MODEL_PROVIDERS["openai"]

def create_client(model_name=DEFAULT_MODEL):
    """
    创建与模型提供商匹配的API客户端
    
    参数:
        model_name (str): 模型名称
    
    返回:
        OpenAI: 配置好的客户端
    """
    provider, config = get_model_provider(model_name)
    
    # 获取API密钥
    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        raise ValueError(f"缺少{config['api_key_env']}环境变量")
    
    # 创建客户端
    client = openai.OpenAI(
        api_key=api_key,
        base_url=config["base_url"]
    )
    
    return client

def generate_news_summary(news_data, tags, model=DEFAULT_MODEL, max_retries=1):
    """
    使用AI模型生成新闻摘要（支持OpenAI、DeepSeek等兼容OpenAI协议的模型）
    
    参数:
        news_data (list): 新闻数据列表
        tags (list): 用户选择的标签
        model (str): 使用的模型名称
        max_retries (int): 最大重试次数
    
    返回:
        generator: 流式返回生成的文本
    """
    # 准备新闻数据
    news_texts = []
    for idx, item in enumerate(news_data):
        title = item.get('title', '')
        description = item.get('description', '')
        source = item.get('source', '')
        url = item.get('url', '')
        
        news_text = f"{idx+1}. {title}\n来源: {source}\n描述: {description}\n链接: {url}\n"
        news_texts.append(news_text)
    
    news_context = "\n".join(news_texts)
    
    # 构建提示词
    prompt = f"""
你是一位专业的新闻分析师和内容策展人。根据以下{len(news_data)}条与"{', '.join(tags)}"相关的新闻，
请对这些新闻进行分类整理并生成一份简洁的摘要报告。

请按以下格式组织你的回复：

## 今日要点
（列出3-5个最重要的新闻要点）

## 主题聚焦
（按主题将新闻分组，突出最重要的发展动态）

## 深度分析
（针对最重要的1-2个话题做简短分析）

新闻数据：
{news_context}

请用中文回复，确保内容准确、客观、简洁。
"""

    tried_models = []
    current_model = model
    retries = 0
    
    while retries <= max_retries:
        try:
            # 记录当前尝试的模型
            tried_models.append(current_model)
            logger.info(f"正在使用模型: {current_model} 生成摘要")
            
            # 识别模型提供商并创建客户端
            provider, _ = get_model_provider(current_model)
            client = create_client(current_model)
            
            # 通用参数
            common_params = {
                "model": current_model,
                "messages": [
                    {"role": "system", "content": "你是一位专业的新闻分析师和内容策展人。你的工作是整理和总结新闻内容，提取重点信息。"},
                    {"role": "user", "content": prompt}
                ],
                "stream": True,
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            # 提供商特定参数调整
            if provider == "deepseek":
                # DeepSeek特定参数，如有需要可添加
                pass
            
            # 创建请求
            stream = client.chat.completions.create(**common_params)
            
            # 返回流式生成结果
            return stream
        
        except Exception as e:
            error_message = str(e)
            retries += 1
            
            # 处理特定错误
            if "unsupported_country_region_territory" in error_message:
                logger.warning(f"地区限制错误: {e}")
                error_message = "当前地区不支持此模型服务。正在尝试备用模型..."
                
                # 尝试备用模型
                if current_model in FALLBACK_MODELS and FALLBACK_MODELS[current_model] not in tried_models:
                    logger.info(f"正在切换到备用模型: {FALLBACK_MODELS[current_model]}")
                    current_model = FALLBACK_MODELS[current_model]
                    continue
            else:
                logger.error(f"调用API时出错: {e}")
            
            # 如果所有重试都失败，返回错误信息
            if retries > max_retries:
                error_details = f"生成摘要时出错: {error_message}\n尝试过的模型: {', '.join(tried_models)}"
                return [{"choices": [{"delta": {"content": error_details}}]}] 