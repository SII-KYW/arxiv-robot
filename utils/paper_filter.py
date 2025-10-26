"""
论文筛选模块
"""

import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class PaperFilter:
    """论文筛选器"""
    
    def __init__(self, keywords: List[str], exclude_keywords: List[str] = None):
        self.keywords = keywords
        self.exclude_keywords = exclude_keywords or []
    
    def filter_papers(self, papers: List[Dict], min_score: float = 1.0) -> List[Dict]:
        """筛选论文"""
        filtered_papers = []
        
        for paper in papers:
            # 检查排除关键词
            text_to_check = f"{paper['title']} {paper['abstract']}".lower()
            if any(keyword.lower() in text_to_check for keyword in self.exclude_keywords):
                continue
            
            # 计算相关性得分
            score = 0
            matched_keywords = []
            
            for keyword in self.keywords:
                if keyword.lower() in text_to_check:
                    matched_keywords.append(keyword)
                    # 标题匹配权重更高
                    if keyword.lower() in paper['title'].lower():
                        score += 3
                    else:
                        score += 1
            
            # 只保留得分高于阈值的论文
            if score >= min_score:
                paper['relevance_score'] = score
                paper['matched_keywords'] = matched_keywords
                filtered_papers.append(paper)
        
        # 按得分排序
        filtered_papers.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"筛选出 {len(filtered_papers)} 篇相关论文")
        return filtered_papers
