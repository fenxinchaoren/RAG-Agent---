from utils.path_tool import get_abs_path
#使用yml，对应的，配置文件（.yml)里是k:v格式
import yaml
import os
#创建rag、向量数据库、提示词、agent四个类型配置文件获取函数
#rag配置文件获取
def load_rag_config(
        #如果不传入路径，默认是这个路径
        #这里不能写config_path:get_abs_path("config/rag.yml")
        config_path:str=get_abs_path("config/rag.yml"),encoding:str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        #打开目标地址，全力加载内容
        return yaml.load(f, Loader=yaml.FullLoader)

def load_chroma_config(
        #如果不传入路径，默认是这个路径
        config_path:str=get_abs_path("config/chroma.yml"),encoding:str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        #打开目标地址，全力加载内容
        return yaml.load(f, Loader=yaml.FullLoader)

def load_prompts_config(
        #如果不传入路径，默认是这个路径
        config_path:str=get_abs_path("config/prompts.yml"),encoding:str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        #打开目标地址，全力加载内容
        return yaml.load(f, Loader=yaml.FullLoader)

def load_agent_config(
        #如果不传入路径，默认是这个路径
        config_path:str=get_abs_path("config/agent.yml"),encoding:str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        #打开目标地址，全力加载内容
        return yaml.load(f, Loader=yaml.FullLoader)

#调用函数，得到返回值.这些变量承载的就是打开yml配置文件里的全部内容
rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()

if __name__ == "__main__":
    print(rag_config['chat_model_name'])