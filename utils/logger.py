"""
美化的日志输出模块
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class SimpleFormatter(logging.Formatter):
    """简化格式的日志格式化器 - 仅用于控制台"""
    
    def format(self, record):
        """格式化日志记录"""
        # 直接返回消息，不添加emoji
        return record.getMessage()


class MarkdownFormatter(logging.Formatter):
    """Markdown格式的日志格式化器 - 用于文件"""
    
    # 日志等级到emoji和颜色的映射
    LEVEL_STYLES = {
        'DEBUG': ('🔍', '\033[36m'),      # 青色
        'INFO': ('✅', '\033[32m'),       # 绿色
        'WARNING': ('⚠️', '\033[33m'),    # 黄色
        'ERROR': ('❌', '\033[31m'),      # 红色
        'CRITICAL': ('💥', '\033[35m'),   # 紫色
    }
    
    def format(self, record):
        """格式化日志记录"""
        # 获取emoji和颜色
        emoji, color = self.LEVEL_STYLES.get(record.levelname, ('📝', '\033[37m'))
        
        # 格式化时间
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建markdown风格的日志
        log_msg = f"{color}{emoji} [{timestamp}] {record.levelname}{color}\n{record.getMessage()}\033[0m"
        
        return log_msg


class APILogger:
    """API调用专用日志记录器"""
    
    def __init__(self, name: str = "API"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
    
    def log_api_call(self, api_name: str, endpoint: str, method: str = "GET", 
                     status: Optional[str] = None, response_data: Optional[dict] = None,
                     error: Optional[str] = None):
        """记录API调用"""
        
        # 只记录详细输出到文件
        if status:
            lines = [
                f"### 🔌 API调用: {api_name}",
                f"",
                f"- **方法**: `{method}`",
                f"- **端点**: `{endpoint}`",
            ]
            
            if status == "success":
                lines.append(f"- **状态**: ✅ 成功")
                if response_data:
                    response_str = str(response_data)
                    if len(response_str) > 500:
                        response_str = response_str[:500] + "..."
                    lines.append(f"- **响应**: ```json\n{response_str}\n```")
            elif status == "failed":
                lines.append(f"- **状态**: ❌ 失败")
                if error:
                    lines.append(f"- **错误**: `{error}`")
            else:
                lines.append(f"- **状态**: ⏳ 进行中...")
            
            lines.append("")
            detailed_message = "\n".join(lines)
            
            # 只记录到文件
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.emit(logging.LogRecord(
                        self.logger.name, logging.INFO, "", 0, detailed_message,
                        (), None))
    
    def log_openai_request(self, model: str, prompt_preview: str, success: bool = False, 
                          error: Optional[str] = None, response_preview: Optional[str] = None):
        """记录OpenAI请求"""
        
        # 只记录详细输出到文件
        lines = [
            f"### 🤖 AI总结请求",
            f"",
            f"- **模型**: `{model}`",
        ]
        
        # 截断过长的提示词预览
        preview = prompt_preview[:200] if len(prompt_preview) > 200 else prompt_preview
        lines.append(f"- **提示词预览**: ```\n{preview}...\n```")
        
        if success:
            lines.append(f"- **状态**: ✅ 成功")
            if response_preview:
                # 截断过长的响应预览
                resp_preview = response_preview[:300] if len(response_preview) > 300 else response_preview
                lines.append(f"- **响应预览**: ```\n{resp_preview}\n```")
        else:
            lines.append(f"- **状态**: ❌ 失败")
            if error:
                # 截断过长的错误信息
                error_short = error[:300] if len(error) > 300 else error
                lines.append(f"- **错误**: `{error_short}`")
        
        lines.append("")
        detailed_message = "\n".join(lines)
        
        # 只记录到文件
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.emit(logging.LogRecord(
                    self.logger.name, logging.INFO, "", 0, detailed_message,
                    (), None))
    
    def log_email_send(self, recipient: str, success: bool = False, error: Optional[str] = None):
        """记录邮件发送"""
        
        # 文件：详细输出
        lines = [
            f"### 📧 邮件发送",
            f"",
            f"- **收件人**: `{recipient}`",
            f"- **状态**: {'✅ 成功' if success else '❌ 失败'}",
        ]
        
        if error:
            lines.append(f"- **错误**: `{error}`")
        
        lines.append("")
        detailed_message = "\n".join(lines)
        
        # 只记录到文件
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.emit(logging.LogRecord(
                    self.logger.name, logging.INFO if success else logging.ERROR, "", 0, detailed_message,
                    (), None))
    
    def log_section(self, title: str, content: str = ""):
        """记录章节标题"""
        lines = [
            f"## {title}",
            "",
        ]
        
        if content:
            lines.append(content)
            lines.append("")
        
        self.logger.info("\n".join(lines))
    
    def log_step(self, step_number: int, step_name: str, status: str = "start"):
        """记录步骤"""
        emoji = {"start": "🚀", "complete": "✅", "failed": "❌"}.get(status, "📝")
        self.logger.info(f"{emoji} 步骤 {step_number}: {step_name}")


def setup_logger(level: str = "INFO"):
    """设置全局日志"""
    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[
            # 文件处理器使用详细格式
            logging.FileHandler('output/arxiv_robot.log', encoding='utf-8'),
        ]
    )
    
    # 为文件handler添加详细格式
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # 为控制台添加简化格式
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(SimpleFormatter())
    root_logger.addHandler(console_handler)

