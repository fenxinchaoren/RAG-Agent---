#提供模型
#继承python里abc里的抽象类
from abc import ABC, abstractmethod
from typing import Optional, Union
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from utils.config_handler import rag_config

class BaseModelFactory(ABC):
    @abstractmethod
    #构造一个抽象的方法叫做generator
        #实现工厂类需要生成器，去生成我们想要的对象，内容是pass，因为是抽象类，不写函数体，只定义函数名称
        #这里我没明白？？？
        #返回值有两类，嵌入模型和聊天模型
    #新版python可以用def generator(self)->Optional[Embeddings|BaseChatModel]:
    def generator(self)->Optional[Union[Embeddings, BaseChatModel]]:
        pass
#构建上面基础类的两个子类，这两个子类肯定是得继承BaseModelFactory的函数
class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Union[Embeddings, BaseChatModel]]:
        return ChatTongyi(model=rag_config['chat_model_name'])
class EmbeddingFactory(BaseModelFactory):
    def generator(self) -> Optional[Union[Embeddings, BaseChatModel]]:
        return DashScopeEmbeddings(model=rag_config['embedding_model_name'])
#创建类实例并拿到模型名称
chat_model=ChatModelFactory().generator()
embed_model=EmbeddingFactory().generator()

#问题：父类和子类的关系是怎样的？为什么最后还是创建了子类实例？完全没有用到父类啊？？？