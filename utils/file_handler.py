import hashlib
import os
from utils.logger_hander import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

#将文件存储进知识库前，需要做去重判断
#将文件转化成md5的16进制字符串，然后判断是否有重复
def get_file_md5_hex(filepath):
    if not os.path.exists(filepath):
        logger.error(f"[md5]计算文件{filepath}不存在")
        return
    if not os.path.isfile(filepath):
        #isfile是什么
        logger.error(f"[md5]计算文件{filepath}不是文件")
        return
    #引入md5方法
    md5_obj=hashlib.md5()
    #不能直接全部加载，要进行分片加载
    chunk_size=4096     #4KB分片，避免文件过大
    #读取文件，将文件字符串转换成md5的16进制格式
    try:
        with open(filepath, 'rb') as f:     #必须采用二进制读取“rb”
            while chunk:= f.read(chunk_size):
                #这里读了就会减少吗？啥意思啊
                md5_obj.update(chunk)
            md5_hex=md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        #下边{str(e)}啥意思
        logger.error(f"[md5]计算文件{filepath}md5失败，{str(e)}")
        #为什么返回none
        return None

#返回文件夹内文件后缀(类型）的文件列表（列表内是文件地址）
def listdir_with_allowed_type(
        #目标文件夹地址,允许类型：元祖
        path:str,allowed_types:tuple[str]
):
    #首先判断给出的地址对应的是否是文件夹
    if not os.path.isdir(path):
        logger.error(f"[获取文件夹下符合类型的文件]{path}不是文件夹")
        #为什么要返回allowed_types
        return allowed_types
    file=[]
    #对应文件夹下每个文件，f是文件名称
    for f in os.listdir(path):
        #判断文件后缀
        if f.endswith(allowed_types):
            #file应该添加满足标准的地址，不应该只是文件名f
            file.append(os.path.join(path, f))
    #为了保存，转换成元祖格式。为什么？
    return tuple(file)
#pdf和txt文档加载器，PDF加载器密码先默认不存在，否则需要传入密码，不然报错
def PDF_loader(filepath:str,password:str=None)->list[Document]:
    return PyPDFLoader(filepath, password).load()
def Txt_loader(filepath:str)->list[Document]:
    #文件加载器需要制定编码
    return TextLoader(filepath,encoding='utf-8').load()