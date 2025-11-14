"""
AI总结模块
"""

import requests
import logging
import re
from typing import Dict
import os
import json

from utils.logger import APILogger

logger = logging.getLogger(__name__)
api_logger = APILogger("OpenAI")


class AISummarizer:
    """AI总结器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', None)
        self.api_url = os.getenv("OPENAI_API_URL", None)
        self.model_type = os.getenv("MODEL_TYPE", "gpt-3.5-turbo")
        self.use_ai_summary = os.getenv("USE_AI_SUMMARY", "TRUE") == "TRUE"
        
        if self.api_key is None or self.api_url is None:
            self.use_ai_summary = False
            
        if self.use_ai_summary:
            logger.info("启用AI总结功能")
        else:
            logger.info("使用基础总结功能（未启用AI或未配置API密钥）")
        
        self.enable_thinking = os.getenv("ENABLE_THINKING", "FALSE") == "TRUE"
    
    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """总结论文"""
        if not self.use_ai_summary:
            return self._basic_summary(abstract)
        
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            system_prompt = f"""
你是一名专业的学术分析助手，擅长从学术论文中提取关键问题、创新点和结论。你需要用简洁、准确、科学的语言，根据提供的论文内容进行分析提取信息。请基于以下要求完成任务：
1. 用中文回答，避免使用不必要的冗长语言；
2. 强调论文技术要点和创新性；
3. 以清晰的结构归纳并输出所需信息。
"""
# 4. 每部分信息不超过100字；

            prompt = f"""
请分析以下学术论文，提取关键信息并回答：
标题: {title}
摘要: {abstract}

请按照以下格式输出：
核心问题：[论文要解决的核心问题]
关键思路：[论文的主要方法和创新点]
主要结论：[论文的主要发现和结果]

（请严格遵循格式要求并用简洁语言表达。）
"""
            
            if not self.enable_thinking:
                if "qwen3" in self.model_type.lower():
                    prompt += "/no_think"
            
            data = {
                "model": self.model_type,
                "messages": [
                    {
                        "role": "system", "content": system_prompt,
                        "role": "user", "content": prompt
                    }
                ],
                "stream": False,
                "enable_thinking": self.enable_thinking,
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            # 检查响应
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 记录成功到文件
                api_logger.log_openai_request(
                    model=self.model_type,
                    prompt_preview=prompt,
                    success=True,
                    response_preview=content
                )
                
                logger.debug(content)
                return self._parse_ai_response(content)
            else:
                # 记录失败到文件
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                api_logger.log_openai_request(
                    model=self.model_type,
                    prompt_preview=prompt,
                    success=False,
                    error=error_msg
                )
                logger.error(f"⚠️ AI总结失败，使用基础总结: HTTP {response.status_code}")
                result = self._basic_summary(abstract)
                result['_ai_failed'] = True  # 标记为失败
                return result
                
        except Exception as e:
            logger.debug(e)
            # 记录异常到文件
            api_logger.log_openai_request(
                model=self.model_type,
                prompt_preview=f"标题: {title[:50]}...",
                success=False,
                error=str(e)
            )
            logger.error(f"⚠️ AI总结失败，使用基础总结: {e}")
            result = self._basic_summary(abstract)
            result['_ai_failed'] = True  # 标记为失败
            return result
    
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
            
            if '核心问题' in line or 'Core Problem' in line:
                current_section = 'core_problem'
                # 移除"核心问题："前缀
                result[current_section] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif '关键思路' in line or 'Key Approach' in line:
                current_section = 'key_approach'
                # 移除"关键思路："前缀
                result[current_section] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif '主要结论' in line or 'Main Conclusion' in line:
                current_section = 'main_conclusion'
                # 移除"主要结论："前缀
                result[current_section] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif current_section and line and not line.startswith('【') and not line.startswith('['):
                # 继续添加到当前section
                result[current_section] += ' ' + line
        
        # 清理每个字段
        for key in result:
            result[key] = result[key].strip()
        
        return result
