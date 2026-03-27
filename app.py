import time

import streamlit as st
from agent.react_agent import ReactAgent

#标题
st.title("智扫通机器人智能客服")
st.divider()        #添加大分隔符
#更改刷新机制,添加缓存
if "agent" not in st.session_state:
    st.session_state["agent"]=ReactAgent()
#保存问答信息
if "message" not in st.session_state:
    st.session_state["message"]=[]

#后边内容是为了把内容保存到缓存，但是每次提问都应该把历史问题都展示在页面
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

#用户提问信息
user_input=st.chat_input()
#如果用户提问不为空
if user_input:
    #在页面上写出用户提问
    st.chat_message("user").write(user_input)
    #历史中添加
    st.session_state["message"].append(
        {"role":"user","content":user_input}
    )
    response_message=[]
    #AI回复信息，添加思考标志，返回迭代器，用生成器接收读取到历史中写到页面上
    with st.spinner("智能客服思考中..."):
        #前边定义了st.session_state["agent"]=ReactAgent()是创造的agent实例
        #利用agent定义的方法将问题输入到智能体中,回复出来一个迭代器，且只能读取一次
        res_stream=st.session_state["agent"].execute_stream(user_input)
        #定义生成器来抓取迭代器
        def capture(generator,cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                #实现流式输出，而不是一段一段流式输出
                for char in chunk:
                    time.sleep(0.01)
                    yield char
        #将迭代器内容保存到生成器中，并且写到页面上
        st.chat_message("assistant").write_stream(capture(res_stream,response_message))
        #将生成器内容保存到st缓存中，用户每次提问每次只保存最后一条，因为其中内容包含很多条
        st.session_state["message"].append({"role":"assistant","content":response_message[-1]})
        #输出过程中可以展示思考过程，输出完毕思考过程应该消失
        #当前历史消息没有思考过程，但是每次回答最后输出结果都有思考过程
        #所以每次输出结尾应该添加刷新
        st.rerun()
