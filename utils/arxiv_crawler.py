"""
arXiv论文爬取模块
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import time

logger = logging.getLogger(__name__)


class ArxivCrawler:
    """arXiv爬虫类"""
    
    def __init__(self, categories: List[str], max_papers_per_category: int = 50):
        self.categories = categories
        self.max_papers_per_category = max_papers_per_category
        self.base_url = "http://export.arxiv.org/api/query"
    
    def fetch_papers(self, days_back: int = 1) -> List[Dict]:
        """从arXiv获取论文"""
        all_papers = []
        
        for category in self.categories:
            try:
                logger.info(f"正在爬取类别 {category}...")
                
                # 构建查询
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                start_str = start_date.strftime("%Y%m%d")
                end_str = end_date.strftime("%Y%m%d")
                
                # 构建查询URL - 优化查询方式
                query_url = f"{self.base_url}?search_query=cat:{category}&max_results={self.max_papers_per_category}&sortBy=submittedDate&sortOrder=descending"
                logger.debug(f"查询URL: {query_url}")
                
                # 发送请求
                response = requests.get(query_url, timeout=30)
                response.raise_for_status()
                
                # 解析响应
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries:
                    paper = {
                        'title': entry.get('title', '').replace('\n', ' ').strip(),
                        'authors': [author.get('name', '') for author in entry.get('authors', [])],
                        'abstract': entry.get('summary', '').replace('\n', ' ').strip(),
                        'published': entry.get('published', ''),
                        'link': entry.get('link', ''),
                        'arxiv_id': entry.get('id', '').split('/')[-1] if entry.get('id') else '',
                        'categories': [tag.get('term', '') for tag in entry.get('tags', [])]
                    }
                    all_papers.append(paper)
                
                logger.info(f"从类别 {category} 获取到 {len(feed.entries)} 篇论文")
                time.sleep(1)  # 避免请求过于频繁
                
            except Exception as e:
                logger.error(f"爬取类别 {category} 时出错: {e}")
        
        # 去重
        unique_papers = {}
        for paper in all_papers:
            if paper['arxiv_id'] and paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        logger.info(f"总共获取到 {len(unique_papers)} 篇不重复的论文")
        return list(unique_papers.values())
