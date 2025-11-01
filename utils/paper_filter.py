"""
论文筛选模块
"""

import logging
import re
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


class PaperFilter:
    """论文筛选器"""
    
    def __init__(
        self, 
        keywords: Union[Dict[str, List[str]], Dict[str, List[List[str]]]],
        global_keywords: List[str] = None,
        global_exclude_keywords: List[str] = None
    ):
        self.keywords = keywords
        self.global_keywords = global_keywords or []
        self.global_exclude_keywords = global_exclude_keywords or []
    
    def filter_papers(self, papers: List[Dict], min_score: float = 1.0, ai_summarizer=None) -> Dict[str, List[Dict]]:
        """筛选论文"""        
        filtered_group_papers = {}
        
        for paper in papers:
            for group_name, word_pairs in self.keywords.items():
                if group_name not in filtered_group_papers:
                    filtered_group_papers[group_name] = []
                
                if isinstance(word_pairs[0], list):
                    # pair for [keywords, exclude_words]
                    keywords, exclude_keywords = word_pairs
                else:
                    # word for [keywords]
                    keywords, exclude_keywords = word_pairs, []
                
                exclude_keywords_ = exclude_keywords + self.global_exclude_keywords
                keywords_ = keywords + self.global_keywords
                
                # 检查排除关键词
                text_to_check = f"{paper['title']} {paper['abstract']}".lower()
                if any(keyword.lower() in text_to_check for keyword in exclude_keywords_):
                    continue
                
                # 计算相关性得分
                score = 0
                matched_keywords = []
                
                for keyword in keywords_:
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
                    filtered_group_papers[group_name].append(paper)
        
        # 按得分排序
        for group_name in filtered_group_papers.keys():
            filtered_group_papers[group_name].sort(key=lambda x: x['relevance_score'], reverse=True)
            logger.info(f"{group_name}类别中筛选出 {len(filtered_group_papers[group_name])} 篇相关论文")
            
        return filtered_group_papers
