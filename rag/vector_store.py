# import sys
# from pathlib import Path
# # 定位到 RAG与Agent开发 目录（当前文件是 rag/vector_store.py，父目录是 RAG与Agent开发）
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))
import os

from langchain_chroma import Chroma

#from LangChain_learn.RAG应用开发.config_data import search_kwargs
from model.factory import embed_model,chat_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from utils.file_handler import PDF_loader,Txt_loader,listdir_with_allowed_type,get_file_md5_hex
from utils.logger_hander import logger
from langchain_core.documents import Document

#创建类，实现向量存储
#需要对应的成员变量，增加init。所有类都有init吗？
class VectorStoreService:
    def __init__(self):
        self.vector_store=Chroma(
            collection_name=chroma_config['collection_name'],
            embedding_function=embed_model,
            persist_directory=chroma_config['persist_directory']
        )
        #递归文本分割器
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=chroma_config['chunk_size'],
            chunk_overlap=chroma_config['chunk_overlap'],
            separators=chroma_config['separators'],
            length_function=len
        )
    #向量库中进行相似搜索
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k":chroma_config['k']})

    #从数据文件读取数据，转为向量存入向量库——这里读取到document，是否需要转化成md5_hex再保存？
    #计算文件的md5去重
    def load_document(self):
        def check_md5_hex(md5_for_check:str):
            if not os.path.exists(get_abs_path(chroma_config['md5_hex_store'])):
                open(get_abs_path(chroma_config['md5_hex_store']),'w',encoding='utf-8').close()
                return False
            with open(get_abs_path(chroma_config['md5_hex_store']),"r",encoding='utf-8') as f:
                for line in f.readlines():
                    line=line.strip()
                    if line==md5_for_check:
                        return True
                return False
        def save_md5_hex(md5_for_check:str):
            with open(get_abs_path(chroma_config['md5_hex_store']),"a",encoding='utf-8') as f:
                f.write(md5_for_check+'\n')
        def get_file_document(read_path:str):
            #将txt和pdf文件加载成document
            if read_path.endswith('txt'):       #list[Document]
                return Txt_loader(read_path)
            if read_path.endswith('pdf'):
                return PDF_loader(read_path)
            return []
        #获取想要读取的文件夹，和文件夹底下的文件地址
        allowed_files_path:list[str]=listdir_with_allowed_type(
            get_abs_path(chroma_config['data_path']),
            #这里报错，listdir_with_allowed_type要求传入元组，但是yaml库里是列表.所以这里必须用tuple转换
            tuple(chroma_config['allow_knowledge_file_type'])
        )
        #获取的是文件地址
        #对于每一个文件，首先将文件地址转换成md5_hex的格式与文件中检索，看是否重复，重复说明已经加载过。
        #未加载过的文件用对应加载器加载出来-列表包含document形式。将document进行切片，保存到向量库中
        #添加这个文件的地址到md5库中，表示这个文件已经被保存处理
        for path in allowed_files_path:
            # 首先获取路径的md5值
            md5_hex=get_file_md5_hex(path)
            #其次与已有的md5中的进行查重，存在就跳过
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库中，跳过")
            #接着将文件内容以document形式加载出来，并保存到向量库中
            try:
               documents:list[Document]=get_file_document(path)
               #进行危险检测，如果得到的文件序列是空的。即这个文件没有内容，跳过——这个continue是跳到哪里？
               if not documents:
                   logger.warring(f"[加载知识库]{path}中没有内容，跳过")
                   #为什么用continue？不用行不行？
                   continue
                #进行切片,引用类实例，引用类实例中的分割函数。所以这个self代表什么？
               split_document=self.spliter.split_documents(documents)
               if not split_document:
                   logger.warring(f"[加载知识库]{path}切片后没有内容，跳过")
                   continue
                #将切片后内容存入向量库
               #这里调用类实例，但是为什么不需要变量接收呢？
               self.vector_store.add_documents(split_document)
               #将文件地址记录到md5库中
               save_md5_hex(md5_hex)
               logger.info(f"[加载知识库]{path}内容加载成功")
            except Exception as e:
                logger.error(f"[加载知识库]{path}内容加载失败，{str(e)}")
                #这里为什么也需要continue？不加行不行？
                continue
if __name__=="__main__":
    #创建类实例
    vs=VectorStoreService()
    #执行这一句，load_document创建data下文件构成的向量知识库
    vs.load_document()
    #根据传入问句进行相似度检索，上边创建了这个函数并传入了k
    retriever=vs.get_retriever()
    #只用到了向量库中embedding嵌入式模型
    res=retriever.invoke("迷路")      #res是一个列表包裹Document格式
    for r in res:
        #r是document格式，取其中文本内容使用page.content
        print(r.page_content)
        print("="*20)











        #txt需要utf-8
        #path  data需要绝对路径