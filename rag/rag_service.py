#构建总结服务类，用户提问，将提问和检索到的资料提供给模型，模型进行总结回复
from langchain_core.output_parsers import StrOutputParser

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
#这两个模板有什么区别，到底选哪个？普通模型 / 简单提示词 → 用 PromptTemplate。聊天模型（ChatTongyi、GPT）→ 推荐用 ChatPromptTemplate
from model.factory import chat_model
from langchain_core.documents import Document

def prompt_print(prompt:str)->str:
    print("="*20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt

#类里为什么要加一个object？可以不加吗？——可以，新版 Python 自动继承 object
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store=VectorStoreService()
        self.retriever=self.vector_store.get_retriever()
        self.prompt_text=load_rag_prompts()
        self.prompt_template= PromptTemplate.from_template(self.prompt_text)
        self.model=chat_model       #这里不能加（）因为这里只需要是个字符串
        #为什么要使用__init__chain的格式？有什么好处？为什么前边可以加上self？这不是一个函数吗，为什么变成self的属性了？
        #把链的创建单独封装。__init__chain 是私有方法，只给内部用。self.xxx 是把它变成类的属性，整个类都能用
        self.chain=self.__init__chain()
    #定义链式结构
    def __init__chain(self):
        chain=self.prompt_template|prompt_print|self.model|StrOutputParser()
        return chain
    #导入相似性检索功能。我不明白这里为什么还要导入一次，明明前边已经有了self.vector_store.get_retriever()
    #外面不用知道 retriever.invoke
    def retriever_docs(self,query:str)->list[Document]:
        return self.retriever.invoke(query)
    #根据提示词prompt_text内容，将需要注入的地方注入问题，激活起前边定义的链式结构，
    # 这样模型根据提问和知识库输入，根据提示词要求，输出的是总结版本的检索内容
    def rag_summarize(self,query:str)->str:
        #接收检索内容
        context_docs=self.retriever_docs(query)
        #用一个字符串承载检索内容加询问，检索内容是list形式，遍历拿到
        #取名context是因为提示词里就是这个
        context=''
        conter=0
        for doc in context_docs:
            conter+=1
            context+=f"[参考文献{conter}:参考资料：{doc.page_content}|参考源数据：{doc.metadata}\n"
        #返回值直接注入到chain中，激活chain
        return self.chain.invoke(
            {
                "input":query,"context":context
            })
if __name__=="__main__":
    rag=RagSummarizeService()
    print(rag.rag_summarize("小户型适合那些扫地机器人？"))

