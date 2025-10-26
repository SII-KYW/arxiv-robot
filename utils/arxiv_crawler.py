"""
arXiv论文爬取模块
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import time

from utils.logger import APILogger

logger = logging.getLogger(__name__)
api_logger = APILogger("arXiv")


class ArxivCrawler:
    """arXiv爬虫类"""
    
    def __init__(self, categories: List[str], max_papers_per_category: int = 50):
        self.categories = categories
        self.max_papers_per_category = max_papers_per_category
        self.base_url = "http://export.arxiv.org/api/query"
    
    def fetch_papers(self, days_back: int = 1) -> List[Dict]:
        """从arXiv获取论文"""
        all_papers = []
        failed_categories = []
        
        total_categories = len(self.categories)
        for idx, category in enumerate(self.categories, 1):
            try:
                # 显示进度
                logger.info(f"正在处理类别 {category} [{idx}/{total_categories}]")
                
                # 构建查询
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                
                # 构建查询URL - 优化查询方式
                query_url = f"{self.base_url}?search_query=cat:{category}&max_results={self.max_papers_per_category}&sortBy=submittedDate&sortOrder=descending"
                
                # 发送请求
                response = requests.get(query_url, timeout=30)
                response.raise_for_status()
                
                # 解析响应
                feed = feedparser.parse(response.text)
                
                # 记录详细日志到文件
                api_logger.log_api_call(
                    api_name="arXiv API",
                    endpoint=query_url,
                    method="GET",
                    status="success",
                    response_data={"论文数": len(feed.entries), "类别": category}
                )
                
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
                    logger.debug(paper)
                    all_papers.append(paper)
                
                logger.info(f"✅ {category}: {len(feed.entries)} 篇论文")
                time.sleep(1)  # 避免请求过于频繁
                
            except Exception as e:
                # 记录失败
                failed_categories.append(category)
                api_logger.log_api_call(
                    api_name="arXiv API",
                    endpoint=query_url,
                    method="GET",
                    status="failed",
                    error=str(e)
                )
                logger.error(f"❌ {category}: {e}")
        
        # 报告失败情况
        if failed_categories:
            logger.warning(f"⚠️ {len(failed_categories)} 个类别爬取失败: {', '.join(failed_categories)}")
        
        # 去重
        unique_papers = {}
        for paper in all_papers:
            if paper['arxiv_id'] and paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        logger.info(f"✅ 总共获取到 {len(unique_papers)} 篇不重复的论文")
        return list(unique_papers.values())
