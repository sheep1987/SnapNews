"""
AI摘要组件
"""
import streamlit as st
import time


def render_summary_container():
    """
    渲染摘要容器
    
    返回:
        placeholder: 用于后续更新的占位符
    """
    st.subheader("📊 AI新闻摘要")
    
    # 创建摘要容器样式
    summary_style = """
    <style>
    .summary-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 20px;
    }
    </style>
    """
    st.markdown(summary_style, unsafe_allow_html=True)
    
    # 创建占位符
    summary_placeholder = st.empty()
    return summary_placeholder


def stream_summary(placeholder, stream):
    """
    流式显示摘要
    
    参数:
        placeholder: 占位符
        stream: 流式响应
    """
    # 初始化空字符串
    summary_text = ""
    
    # 添加提示
    placeholder.markdown("""
    <div class="summary-container">
    正在分析新闻数据，请稍候...
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 处理流式输出
        for chunk in stream:
            # 尝试不同的响应格式
            try:
                # 标准OpenAI响应格式
                content = chunk.choices[0].delta.content
            except (AttributeError, IndexError):
                try:
                    # 可能的替代格式1
                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                except (AttributeError, IndexError):
                    try:
                        # 可能的替代格式2 (如果DeepEek使用不同的响应结构)
                        if hasattr(chunk, 'content'):
                            content = chunk.content
                        elif isinstance(chunk, dict):
                            content = chunk.get('content', '')
                        else:
                            content = str(chunk)
                    except:
                        content = ''
            
            if content:
                summary_text += content
                placeholder.markdown(f"""
                <div class="summary-container">
                {summary_text}
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.01)  # 添加小延迟以平滑显示效果
    except Exception as e:
        placeholder.markdown(f"""
        <div class="summary-container">
        生成摘要时出错: {str(e)}
        </div>
        """, unsafe_allow_html=True)
    
    # 添加完成提示
    if summary_text:
        st.success("AI摘要生成完成")


def render_empty_summary():
    """
    渲染空摘要提示
    """
    st.info("选择标签并点击「获取新闻」按钮生成AI摘要") 