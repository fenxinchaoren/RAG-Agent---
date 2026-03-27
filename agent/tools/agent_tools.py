import json
from langchain_core.tools import tool
from utils.logger_hander import logger
from rag.rag_service import RagSummarizeService
import random
from utils.path_tool import get_abs_path
import os
from utils.prompt_loader import load_report_prompts
from pydantic import BaseModel, Field

from utils.config_handler import agent_config
import requests
from dotenv import load_dotenv
from utils.path_tool import get_abs_path

class FetchDataInput(BaseModel):
    tool_input: str = Field(description="JSON格式的输入，包含 user_id 和 month。例如: {'user_id':'1001', 'month':'2025-01'}")
rag=RagSummarizeService()
user_ids=["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010"]
month_arr=["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06","2025-07",
           "2025-08","2025-09","2025-10","2025-11","2025-12"]
#避免获取的外部数据在函数的return中来回返回，定义一个全局变量去接收
external_data={}
@tool(description="从向量存储中检索参考资料")
def rag_summarize(query:str)->str:
    return rag.rag_summarize(query)

load_dotenv(get_abs_path("config.env"))
AMAP_KEY=os.getenv("AMAP_KEY")
IP_API_URL =os.getenv('IP_API')
@tool(description="获取用户所在城市名称，以纯字符串的形式输出")
def get_user_location()->str:
    #准备请求参数，必须包含key——直接用IP_API_URL不行吗？
    #不要拼接 URL：requests.get(url, params=params) 是最佳实践。它会自动帮你处理 ?、& 以及特殊字符的转义
    params = {
        "key": AMAP_KEY,
        "ip": "114.247.50.2"  # 随便找一个北京的公网 IP
    }
    try:
        #发送get请求
        # requests 会自动把 URL 和 params 拼接成：
        # https://restapi.amap.com/v3/ip?key=2427d1d92ae740e88019cdf1a8795f2d4
        response = requests.get(IP_API_URL, params=params, timeout=5)
        #解析返回的JSON数据
        data=response.json()
        #根据高德 API 规范判断状态 (status '1' 表示成功)
        if data.get("status") == "1":
            city = data.get("city")
            #1、获取到城市不为空且城市类型为字符串，返回城市
            if isinstance(city, str) and city:
                return city
            # 2、城市为空，获取省份
            province = data.get("province")
            if isinstance(province, str) and province:
                return province
            #3、都不行，返回兜底
            return "位置获取成功但无法精确到城市"
        else:
            return f"定位失败，原因：{data.get('info')}"
    except Exception as e:
        return f"请求定位接口时发生异常: {str(e)}"

#传入 city（城市编码或城市名）和 key,返回实况天气
WEATHER_API_URL = os.getenv('Weather_API')
@tool(description="获取制定城市天气，以消息字符串的形式返回")
def get_weather(city:str)->str:
    #1、如果没有传入城市，先用定位工具获取到城市
    if not city:
        city = get_user_location().func
        if "失败" in city or "未知" in city:
            return f"自动定位失败，请手动输入城市名称。详情：{city}"
    #2、准备请求参数
    params = {
        "key": AMAP_KEY,
        "city": city,
        "extensions": "base"  # base: 实况天气; all: 预报天气
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        data=response.json()
        if data.get("status") == "1" and data.get("lives"):
            # 高德返回的是一个列表，取第一个元素
            live = data["lives"][0]
            report = (
                f"城市：{live['province']}-{live['city']}\n"
                f"天气：{live['weather']}\n"
                f"气温：{live['temperature']}℃\n"
                f"风向：{live['winddirection']}风\n"
                f"风力：{live['windpower']}级\n"
                f"湿度：{live['humidity']}%")
            return report
        else:
            return f"获取{city}天气失败，原因：{data.get('info', '未知错误')}"

    except Exception as e:
        return f"请求天气接口异常: {str(e)}"






@tool(description="获取用户ID，以纯字符串的形式输出")
def get_user_id()->str:
    return random.choice(user_ids)
@tool(description="获取当前月份，以纯字符串的形式输出")
def get_correct_month()->str:
    return random.choice(month_arr)

#从csv文件中读到外部数据
def generate_external_data():
    """
    {"user_ids:{
                "month":{"特征":xxx,"效率":xxx},
                "month":{"特征":xxx,"效率":xxx},
                "month":{"特征":xxx,"效率":xxx},
                }，
    "user_ids:{
                "month":{"特征":xxx,"效率":xxx},
                "month":{"特征":xxx,"效率":xxx},
                "month":{"特征":xxx,"效率":xxx},
                }
                }
    :return:
    """
    #只有第一次才会把外部数据字典填充完整，其他时刻直接调用即可。所以字典不为空就是填充完整的
    if not external_data:
        #获取到外部数据的地址
        external_data_path = get_abs_path(agent_config['external_data_path'])
        #外部数据地址不存在报错
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")
        with open(external_data_path, "r", encoding="utf-8") as f:
            #只要数据部分，表头不要
            for line in f.readlines()[1:]:
                arr:list[str]= line.strip().split(",")      #先将每一行前后空格去掉，然后将逗号作为分隔符切分这行数据
                user_id:str= arr[0].replace('"',"") #抽取出用户id，将双引号去除——为什么要去除双引号？要的不就是字符串吗？
                feature:str= arr[1].replace('"',"")
                efficiency:str= arr[2].replace('"',"")
                consumables:str= arr[3].replace('"',"")
                comparison:str= arr[4].replace('"',"")
                time:str= arr[5].replace('"',"")
                #如果这行的id不在外部数据检索集合里，说明得创建一个这个id的集合
                if user_id not in external_data:
                    external_data[user_id]= {}
                #有这个id，那么就要为其中添加month相关信息,每人每月的信息只有一条，所以不用判断，直接添加
                external_data[user_id][time]={
                    "特征":feature,
                    "效率":efficiency,
                    "耗材":consumables,
                    "对比":comparison,
                }

# 2. 修改工具函数：只接收 tool_input
@tool(args_schema=FetchDataInput)
def fetch_external_data(tool_input: str) -> str:
    """从外部系统获取指定用户在指定月份的使用记录。"""

    # 初始化变量
    user_id = ""
    month = ""

    # 手动解析这个单一的字符串输入
    try:
        # 处理可能出现的单引号/双引号问题
        clean_json = tool_input.replace("'", '"')
        data = json.loads(clean_json)
        user_id = str(data.get("user_id", ""))
        month = str(data.get("month", ""))
    except Exception:
        # 如果不是 JSON 格式，尝试直接当作 user_id 处理（兼容单参数情况）
        user_id = tool_input
        month = ""

    # 执行原有业务逻辑

    #首先生成外部数据集合
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:        #这里什么时候用KeyError，什么时候用其他？
        #尝试从字典（Dict）中获取一个不存在的键时，Python 会抛出 KeyError
        logger.warning(f"[抓取外部数据]未能检索到用户{user_id}在{month}的使用记录数据")
        return ''       #必须返回''吗？返回None可以吗——不可以，因为Agent / LLM 只认识字符串，返回 None 会直接报错、解析失败！

@tool(description="无入参，无返回值，调用后触发中间键自动为报告生成的场景注入上下文信息，为后续提示词切换提供上下文")
def fill_context_for_report():
    #这个工具啥都没有，到底怎么执行的？
    # return "fill_context_for_report已调用"
    # 获取真正的报告生成要求
    report_rules = load_report_prompts()
    return f"已切换至报告模式。接下来的 Final Answer 请务必严格遵守以下要求：\n{report_rules}"



if __name__ == '__main__':
    #普通函数：接受多个参数 (user_id, month)。
    # BaseTool 对象：它的 __call__ 或 run 方法期望接收一个输入（通常是字典或字符串）
    # print(fetch_external_data.func("1001","2025-03"))

    print(get_user_location.func())
    print(get_weather.func(get_user_location.func()))