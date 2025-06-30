# MCP文档总结工具

一个Python程序，用于爬取https://mcp-docs.cn/网站内容并使用deepseek-chat模型进行总结。

## 功能特性

- 自动爬取MCP文档网站内容
- 支持三种总结详细程度配置
- 结果保存为JSON格式
- 详细的日志记录

## 安装与配置

1. 克隆本仓库
2. 安装依赖：
   ```bash
   uv run main.py
   ```
   会自动安装依赖，并且创建虚拟环境
3. 复制`.env.example`为`.env`并配置API密钥：
   ```bash
   cp .env.example .env
   ```
   编辑`.env`文件，添加你的Deepseek API密钥

## 使用方法

基本命令：
```bash
python main.py
```

可选参数：
```
--detail [1-3]      总结详细程度 (1=简略, 2=中等, 3=详细)
--max-pages NUM     最大爬取页面数 (默认50)
--output FILE       输出文件名 (默认summary.json)
```

示例：
```bash
# 详细总结前20个页面
python main.py --detail 3 --max-pages 20 --output my_summary.md
```

## 输出格式

总结结果保存为md格式

## 注意事项

1. 请确保你有权限爬取目标网站
2. API调用可能会产生费用，请关注使用量
3. 程序运行日志保存在`mcp_summarizer.log`中