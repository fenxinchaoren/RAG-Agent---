from utils.path_tool import get_abs_path
from utils.logger_hander import logger
from utils.config_handler import prompts_config

def load_system_prompts():
    #获得系统提示词地址
    try:
        system_prompts_path=get_abs_path(prompts_config["main_prompt_path"])
    except FileNotFoundError:
        #教程里用的except keyError as e:，有什么区别吗
        logger.error(f"[获取系统提示词地址]出错，在yaml配置项中没有main_prompt_path配置项")
        # 教程里用的raise e
    #获得系统提示词内容
    try:
        #.read()是啥，里边有r不就可以代替读了吗？
        return open(system_prompts_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[加载系统提示词内容]出错，解析系统提示词内容出错，{str(e)}")
        raise e
def load_rag_prompts():
    #获得系统提示词地址
    try:
        rag_summarize_path=get_abs_path(prompts_config["rag_summarize_prompt_path"])
    except FileNotFoundError:
        #教程里用的except keyError as e:，有什么区别吗
        logger.error(f"[获取rag总结提示词地址]出错，在yaml配置项中没有rag_summarize_prompt_path配置项")
        # 教程里用的raise e
    #获得系统提示词内容
    try:
        #.read()是啥，里边有r不就可以代替读了吗？
        return open(rag_summarize_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[加载rag总结提示词内容]出错，解析rag总结提示词内容出错，{str(e)}")
        raise e
def load_report_prompts():
    #获得系统提示词地址
    try:
        report_prompt_path=get_abs_path(prompts_config["report_prompt_path"])
    except FileNotFoundError:
        #教程里用的except keyError as e:，有什么区别吗
        logger.error(f"[获取report提示词地址]出错，在yaml配置项中没有report_prompt_path配置项")
        # 教程里用的raise e
    #获得系统提示词内容s
    try:
        #.read()是啥，里边有r不就可以代替读了吗？
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[加report统提示词内容]出错，解析report提示词内容出错，{str(e)}")
        raise e

if __name__ == "__main__":
    print(type(load_system_prompts()),load_system_prompts())
