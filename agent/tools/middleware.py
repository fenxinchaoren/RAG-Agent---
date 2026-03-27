import os
from typing import Callable, Union, Any, Dict

# 基础导入修复
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from utils.prompt_loader import load_system_prompts, load_report_prompts
from utils.logger_hander import logger

# 消息与工具相关
from langchain_core.messages import ToolMessage, BaseMessage, AIMessage
from langchain_core.runnables import RunnableConfig


# 1. 定义状态 (取代原本飘红的 AgentState)
class AgentState(Dict):
    messages: list[BaseMessage]
    context: Dict[str, Any]


# 2. 工具监控逻辑 (手动包装，不依赖不存在的 @wrap_tool_call)
def monitor_tool_logic(state: AgentState):
    """
    在 LangGraph 中，我们通常在 ToolNode 执行前后记录日志。
    如果你需要拦截工具调用，可以在 Node 逻辑中处理。
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            logger.info(f"[工具监控] 准备执行：{tool_call['name']}")
            logger.info(f"[工具监控] 执行参数：{tool_call['args']}")

            # 模拟原代码中的 fill_context_for_report 逻辑
            if tool_call['name'] == "fill_context_for_report":
                state["context"]["report"] = True
                logger.info("[状态标记] 已切换为报告模式")
    return state


# 3. 动态提示词切换逻辑 (取代飘红的 @dynamic_prompt)
def get_model_prompt(state: AgentState):
    """
    根据 state 中的 context 决定使用哪个 prompt
    """
    is_report = state.get("context", {}).get("report", False)
    if is_report:
        logger.info("[提示词切换] 使用报告生成模版")
        return load_report_prompts()

    logger.info("[提示词切换] 使用系统默认模版")
    return load_system_prompts()


# 4. 辅助函数：模型执行前的日志
def log_before_model(state: AgentState):
    msg_count = len(state.get("messages", []))
    last_msg = state["messages"][-1] if msg_count > 0 else "None"

    logger.info(f"[模型输出前] 消息条数: {msg_count}")
    if hasattr(last_msg, 'content'):
        # 使用 __class__.__name__ 代替 type(...).__name__ 同样有效
        logger.debug(f"消息类型: {last_msg.__class__.__name__}, 内容: {last_msg.content[:50]}...")
    return state


# 示例：如何整合到 Agent 类中
class ReactAgent():
    def __init__(self):
        # 这里的初始化需要配合你项目的逻辑
        pass


if __name__ == '__main__':
    # 简单的环境自检
    print("代码路径修复完成，请确保执行了 pip install -U langgraph")