"""
AI总结模块
"""

import requests
import logging
import re
from typing import Dict
import os
import json

logger = logging.getLogger(__name__)


class AISummarizer:
    """AI总结器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.api_url = os.getenv("OPENAI_API_URL", None)
        self.model_type = os.getenv("MODEL_TYPE", "gpt-3.5-turbo")
        self.use_ai_summary = os.getenv("USE_AI_SUMMARY", True)
        
        if not self.api_key or self.api_url is None:
            self.use_ai_summary = False
        logger.info(f"Initialize `AISummarizer` and set `USE_AI_SUMMARY` to {self.use_ai_summary}")
        
        self.enable_thinking = os.getenv("ENABLE_THINKING", False)
    
    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """总结论文"""
        if not self.use_ai_summary:
            return self._basic_summary(abstract)
        
        try:
            # headers = {
            #     'Authorization': f'Bearer {self.api_key}',
            #     'Content-Type': 'application/json'
            # }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
                        
            prompt = f"""
请分析以下学术论文，提取关键信息：

标题: {title}
摘要: {abstract}

请按以下格式输出：
核心问题：[论文要解决的核心问题]
关键思路：[论文的主要方法和创新点]
主要结论：[论文的主要发现和结果]

要求：
1. 用中文回答
2. 每个部分控制在100字以内
3. 突出技术要点和创新性
"""
            
            data = {
                "model": self.model_type,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                # "max_tokens": 500,
                # "temperature": 0.3
                "enable_thinking": self.enable_thinking,
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                # timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.debug(content)
                return self._parse_ai_response(content)
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return self._basic_summary(abstract)
                
        except Exception as e:
            logger.error(f"AI总结失败: {e}")
            return self._basic_summary(abstract)
    
    def _basic_summary(self, abstract: str) -> Dict[str, str]:
        """基础总结"""
        sentences = re.split(r'[.!?]+', abstract)
        return {
            'core_problem': sentences[0].strip() if sentences else abstract[:200],
            'key_approach': sentences[1].strip() if len(sentences) > 1 else abstract[200:400],
            'main_conclusion': sentences[-1].strip() if sentences else abstract[-200:]
        }
    
    def _parse_ai_response(self, content: str) -> Dict[str, str]:
        """解析AI响应"""
        result = {'core_problem': '', 'key_approach': '', 'main_conclusion': ''}
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '核心问题' in line:
                current_section = 'core_problem'
                result[current_section] = line.split('：', 1)[-1].strip()
            elif '关键思路' in line:
                current_section = 'key_approach'
                result[current_section] = line.split('：', 1)[-1].strip()
            elif '主要结论' in line:
                current_section = 'main_conclusion'
                result[current_section] = line.split('：', 1)[-1].strip()
            elif current_section and line:
                result[current_section] += ' ' + line
        
        return result
