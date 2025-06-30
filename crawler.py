from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import logging

class MCPDocsCrawler:
    """MCP文档爬取器"""
    
    def __init__(self, base_url="https://mcp-docs.cn/", similarity_threshold=0.9):
        self.base_url = base_url
        self.visited_urls = set()
        self.content_hashes = set()
        self.similarity_threshold = similarity_threshold
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCPDocsSummarizer/1.0'
        })
        
    def crawl(self, max_pages=50):
        """爬取网站内容
        
        Args:
            max_pages: 最大爬取页面数
            
        Returns:
            tuple: (页面列表, 统计信息字典)
            页面列表: 包含页面标题、URL和内容的字典列表
            统计信息: {
                'total_pages': 总页面数,
                'content_lengths': 每个页面的内容长度列表,
                'total_length': 所有页面总内容长度,
                'duplicates_removed': 移除的重复页面数
            }
        """
        self.visited_urls = set()
        self.content_hashes = set()
        pages = []
        duplicates_removed = 0
        
        # 使用栈代替递归，避免深度限制
        stack = [(self.base_url, False)]
        
        while stack and len(pages) < max_pages:
            url, is_processed = stack.pop()
            
            if is_processed:
                # 处理页面内容
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else "无标题"
                    content = self._extract_content(soup)
                    
                    # 计算内容哈希并检查重复
                    content_hash = self._calculate_content_hash(content)
                    if content_hash in self.content_hashes:
                        duplicates_removed += 1
                        continue
                        
                    self.content_hashes.add(content_hash)
                    pages.append({
                        'title': title,
                        'url': url,
                        'content': content
                    })
                    logging.info(f"爬取成功: {url} - 标题: {title}")
                    
                except Exception as e:
                    logging.error(f"爬取 {url} 失败: {str(e)}")
                    
            else:
                # 添加到已访问集合
                if url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                
                # 获取页面链接
                try:
                    response = self.session.get(url, timeout=5)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        next_url = urljoin(self.base_url, link['href'])
                        if next_url.startswith(self.base_url):
                            stack.append((next_url, False))
                            
                    # 标记为待处理
                    stack.append((url, True))
                    
                except Exception as e:
                    logging.error(f"获取 {url} 链接失败: {str(e)}")
        
        # 计算统计信息
        content_lengths = [len(p['content']) for p in pages]
        stats = {
            'total_pages': len(pages),
            'content_lengths': content_lengths,
            'total_length': sum(content_lengths),
            'duplicates_removed': duplicates_removed
        }
        
        return pages, stats
        
    def _calculate_content_hash(self, content):
        """计算内容哈希值用于去重
        
        Args:
            content: 页面内容字符串
            
        Returns:
            str: 内容的MD5哈希值
        """
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def _extract_content(self, soup):
        """从页面中提取主要内容"""
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'aside', 'header']):
            element.decompose()
            
        # 优先查找文章主体内容
        main_content = (soup.find('article') or 
                      soup.find('main') or 
                      soup.find('div', class_='content') or 
                      soup.body)
                      
        if not main_content:
            return ""
            
        # 获取文本并清理
        text = main_content.get_text(separator='\n', strip=True)
        
        # 进一步清理空白和空行
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)