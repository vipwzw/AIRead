import argparse
import json
import logging
import os
from pathlib import Path
from crawler import MCPDocsCrawler
from openai_client import DeepseekClient

def setup_logging():
    """配置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mcp_summarizer.log'),
            logging.StreamHandler()
        ]
    )
    # 添加日志分隔线
    logging.info("=" * 80)
    logging.info(" MCP文档爬取与总结任务 ".center(80, '='))
    logging.info("=" * 80)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='MCP文档总结工具')
    parser.add_argument('--detail', type=int, choices=[1, 2, 3], default=2,
                       help='总结详细程度 (1=简略, 2=中等, 3=详细)')
    parser.add_argument('--max-pages', type=int, default=50,
                       help='最大爬取页面数 (默认50)')
    parser.add_argument('--output', type=str, default='summary.json',
                       help='输出文件名 (默认summary.json)')
    return parser.parse_args()

def main():
    """主程序入口"""
    setup_logging()
    args = parse_args()
    
    try:
        # 初始化组件
        crawler = MCPDocsCrawler()
        summarizer = DeepseekClient()
        
        # 爬取文档
        logging.info(f"开始爬取，最多{args.max_pages}个页面...")
        pages, stats = crawler.crawl(args.max_pages)
        logging.info(f"成功爬取 {stats['total_pages']} 个页面")
        logging.info(f"移除重复内容: {stats['duplicates_removed']} 个页面")
        logging.info(f"页面内容长度统计:")
        logging.info(f"- 最短: {min(stats['content_lengths'])} 字符")
        logging.info(f"- 最长: {max(stats['content_lengths'])} 字符")
        logging.info(f"- 平均: {sum(stats['content_lengths']) // stats['total_pages']} 字符")
        logging.info(f"- 总计: {stats['total_length']} 字符")
        
        # 总结内容
        results = []
        for page in pages:
            logging.info(f"总结: {page['title']}")
            summary = summarizer.summarize(
                page['content'],
                detail_level=args.detail
            )
            results.append({
                'title': page['title'],
                'url': page['url'],
                'summary': summary
            })
        
        # 保存结果为Markdown格式
        output_path = Path('summary.md')
        with output_path.open('w', encoding='utf-8') as f:
            f.write("# MCP文档总结报告\n\n")
            f.write("## 统计信息\n")
            f.write(f"- 总爬取页面数: {stats['total_pages']}\n")
            f.write(f"- 移除重复内容数: {stats['duplicates_removed']}\n")
            f.write(f"- 最短内容长度: {min(stats['content_lengths'])} 字符\n")
            f.write(f"- 最长内容长度: {max(stats['content_lengths'])} 字符\n")
            f.write(f"- 平均内容长度: {sum(stats['content_lengths']) // stats['total_pages']} 字符\n")
            f.write(f"- 总内容长度: {stats['total_length']} 字符\n\n")
            
            f.write("## 页面总结\n")
            for result in results:
                f.write(f"### {result['title']}\n")
                f.write(f"- **URL**: {result['url']}\n")
                f.write(f"- **总结**: \n{result['summary']}\n\n")
        
        logging.info(f"总结结果已保存到 {output_path}")
        
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
        raise

if __name__ == '__main__':
    main()