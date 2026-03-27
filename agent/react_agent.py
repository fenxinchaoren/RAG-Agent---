from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from model.factory import chat_model
# 假设你的工具和加载器已经定义好
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_id, get_user_location,
                                     get_correct_month, fetch_external_data, fill_context_for_report)


class ReactAgent():
    def __init__(self):
        # 1. 定义工具列表
        self.tools = [rag_summarize, get_weather, get_user_id, get_user_location,
                      get_correct_month, fetch_external_data, fill_context_for_report]

        # 2. 获取 Prompt 模板
        # 注意：ReAct 代理必须包含 {tools}, {tool_names}, {agent_scratchpad} 三个变量
        # 如果你的 load_report_prompts() 返回的不是标准 ReAct 格式，请参考下面的模板
        # --- 核心修改点：合并提示词 ---
        # 1. 获取你写的那些业务逻辑（客服身份、报告流程等）
        business_rules = load_system_prompts()

        # 2. 构造符合 ReAct 协议的完整模板
        # 注意：这里必须手动加上 {tools}, {tool_names}, {agent_scratchpad}
        full_template = business_rules + """

        你可以使用以下工具：
        {tools}

        请严格遵守以下输出格式：

        Question: 你必须回答的输入问题
        Thought: 思考该做什么
        Action: [{tool_names}] 中的一个
        Action Input: 工具的输入（如果是 fetch_external_data，请使用 JSON 格式 {{"user_id": "xxx", "month": "xxx"}}）
        Observation: 工具返回的结果
        ... (这个 Thought/Action/Action Input/Observation 可以重复多次)
        Thought: 我现在知道最终答案了
        Final Answer: 最终的自然语言回答

        开始！

        Question: {input}
        Thought: {agent_scratchpad}"""

        self.prompt = PromptTemplate.from_template(full_template)

        # 3. 创建底层的 Agent 逻辑 (决定下一步做什么)
        self.inner_agent = create_react_agent(
            llm=chat_model,
            tools=self.tools,
            prompt=self.prompt
        )

        # 4. 创建执行器 (真正循环调用工具并处理状态的部分)
        self.agent_executor = AgentExecutor(
            agent=self.inner_agent,
            tools=self.tools,
            verbose=True,  # 建议设为 True，这样你能在控制台看到它的思考过程
            handle_parsing_errors=True  # 自动处理模型输出格式不规范的问题
        )

    def _get_react_prompt(self):
        template = """尽力回答以下问题。你可以使用以下工具：

{tools}

请使用以下格式：

Question: 你必须回答的输入问题
Thought: 你应该总是思考该做什么
Action: 要采取的动作，应该是 [{tool_names}] 之一
Action Input: 动作的输入。如果是 fetch_external_data，请务必写成 JSON 字符串，例如：{{"user_id": "1001", "month": "2025-01"}}
Observation: 动作的结果
... (这个 Thought/Action/Action Input/Observation 可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终回答

开始！

Question: {input}
Thought: {agent_scratchpad}"""
        return PromptTemplate.from_template(template)
    def execute_stream(self, query: str):
        # AgentExecutor 的输入键通常是 "input"
        input_dict = {"input": query}

        # 使用 agent_executor.stream 进行流式迭代
        for chunk in self.agent_executor.stream(input_dict):
            # AgentExecutor 的 stream 会返回中间步骤和最终结果
            # 我们只提取最终答案部分 ("output")
            if "output" in chunk:
                yield chunk["output"] + '\n'


if __name__ == '__main__':
    agent = ReactAgent()
    # 测试 query
    query_text = ("我的城市是哪里？天气怎么样？机器人应该如何保养？")

    print("--- 正在生成回复 ---")
    for chunk in agent.execute_stream(query_text):
        print(chunk, end='', flush=True)