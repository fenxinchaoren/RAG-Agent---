#为整个工程提供统一的绝对路径。相对路径可能出错
import os

#定义获取工程所在的根目录
def get_project_root():
    #以现在的这个路径配置文件为基准，所有相对路径是在RAG与Agent开发这个文件夹上的
    #所以对于当前来说，根目录是向上找两层
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#将根目录路径和文件相对路径拼接,相对路径是传入的
def get_abs_path(project_rev_path:str):
    project_abs_path=get_project_root()
    return os.path.join(project_abs_path,project_rev_path)
if __name__=="__main__":
    path=get_abs_path("config\config.txt")
    print(path)
