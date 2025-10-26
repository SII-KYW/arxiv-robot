"""
AI总结模块
"""

import requests
import logging
import re
from typing import Dict
import os

logger = logging.getLogger(__name__)


class AISummarizer:
    """AI总结器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
    
    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """总结论文"""
        if not self.api_key:
            return self._basic_summary(abstract)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
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
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                'https://api.openai99.top/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
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
