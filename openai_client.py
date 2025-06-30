import os
import openai
from dotenv import load_dotenv
import time
import logging

class DeepseekClient:
    """Deepseek API客户端"""
    
    def __init__(self):
        load_dotenv()  # 加载.env文件
        
    def summarize(self, text, detail_level=2, max_retries=3):
        """使用deepseek-chat模型总结文本
        
        Args:
            text: 要总结的文本
            detail_level: 总结详细程度 (1-3)
            max_retries: 最大重试次数
            
        Returns:
            str: 总结结果
            
        Raises:
            Exception: API调用失败
        """
        prompt = self._build_summary_prompt(text, detail_level)
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                response = openai.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个专业的文档总结助手"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=self._get_max_tokens(detail_level)
                )
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                wait_time = min(2 ** retry_count, 10)  # 指数退避
                logging.warning(f"API调用失败 (尝试 {retry_count}/{max_retries}), {last_error}")
                time.sleep(wait_time)
                
        raise Exception(f"API调用失败，重试{max_retries}次后仍出错: {last_error}")
        
    def _build_summary_prompt(self, text, detail_level):
        """构建总结提示词"""
        detail_descriptions = {
            1: "简要总结",
            2: "总结主要内容",
            3: "详细总结，保留关键细节"
        }
        return f"""请根据以下文本内容，{detail_descriptions.get(detail_level, '')}：
        
        {text[:100000]}  # 限制输入长度
        """
        
    def _get_max_tokens(self, detail_level):
        """根据详细程度获取最大token数"""
        return {
            1: 2000,
            2: 5000,
            3: 10000
        }.get(detail_level, 5000)