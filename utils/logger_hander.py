import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")
# 确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)
# 日志的格式配置  error info debug
DEFAULT_LOG_FORMAT = logging.Formatter(
    #时间、名称、级别、文件名称：行数、信息类型
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
def get_logger(
        #名称，也可以后期传入
        name: str = "agent",
        #控制台日志打印级别，例如这里选了INFO，就不会打印DEBUG级别的日志
        console_level: int = logging.INFO,
        #文件日志打印级别（存入文件）
        file_level: int = logging.DEBUG,
        #可选参数。让你既能自动用，也能自定义日志文件。
        log_file = None,
) -> logging.Logger:    #输出logging里logger类型模块
    #创建一个日志器。每个日志器有唯一名字，这里叫 agent，全局所有文件都可以用同一个日志器
    logger = logging.getLogger(name)
    #设置日志类型
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler。其他文件也会调用日志，但是一个项目使用一个日志即可，多个日志会产生重复创建
    #如果你在 10 个文件里 import logger，会一个日志打印10遍
    if logger.handlers:
        return logger
    # 创建控制台Handler
    console_handler = logging.StreamHandler()
    #设置日志级别
    console_handler.setLevel(console_level)
    #设置日志格式
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    #添加日志，选择控制台类型
    logger.addHandler(console_handler)
    # 文件Handler
    if not log_file:        # 日志文件的存放路径
        #这只是判断有没有路径，并没有创建啊？
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    #存在文件日志路径
    #这创建文件，创建一个 “文件输出处理器”。就按照上面的路径log_file创建
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger
# 快捷获取日志器。其他文件调用logger即可
logger = get_logger()
if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
