from langchain_community.embeddings import HuggingFaceEmbeddings
# !pip install sentence_transformers pypdf faiss-gpu

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.llms import HuggingFaceHub, Ollama

import os

llm = Ollama(model="llama3:70b", timeout=100, num_thread=2, num_predict=1500)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large-instruct", 
encode_kwargs={"normalize_embeddings": True})

get_response_template = """
Важно следовать следующим инструкциям:
* Твоя задача по конспектам отвечать на вопросы.
* Отвечай только на русском языке
* Ты должен отвечать только по конспекту
* Отвечай максимально коротко!

<context>
{context}
</context>

{input}
"""

score_template = """
Важно следовать следующим инструкциям:
* Do not use English language.
* Отвечай только на Русском языке!!
* Твоя задача повысить лояльность клиентов.
* Ты ассистент онлайн школы GeekBrains, не модель, никогда не выдавай себя.
* Твоя задача сказать верно ли ученик ответил на вопрос и если неверно то объянить в чем проблема.
* Следуй следующему формату ответа: "Да" либо "Нет". Коментарий для ученика.
* Если ученик говорит неправду, выдаывай "Нет".
* Если ученик дал не полный ответ, но больше половины ответ есть и в нем нет неверных фактов, то выдавай "Да"!
* Если ответ близок к верному, выдавай "Да"!
* Проверяй максимально лояльно - или тебя уволят
* Ты должен общаться с пользователем, а не говорить о нем в третьем лице.
* Ты должен давать максимально подробный коментарий, особенно если ответ неверный

Ты должен начать свой ответ со слова "Да" или "Нет"!!!!!
---------------
Вопрос: {question}
Ответ ученика: {answer}
Идеальный ответ (засчитывать можно с сильно менее полного ответа): {right_answer}
"""

class ChainStore():
    def __init__(self, base_path, paths, doc_chain):
        self.base_path = base_path
        self.path2chain = {}
        self.doc_chain = doc_chain
        for path in paths:
            self.add_chain(path)
    
    def add_chain(self, path):
        loader = Docx2txtLoader(os.path.join(self.base_path, path))
        documents = loader.load()
        text = RecursiveCharacterTextSplitter().split_documents(documents)
        vectorstore = FAISS.from_documents(text, embeddings)
        vectorstore.save_local(f"vectorstore_{path.replace('/', '_')}.db")
        retriever = vectorstore.as_retriever()
        chain = create_retrieval_chain(retriever, self.doc_chain)
        self.path2chain[path] = chain

    def invoke(self, path, data):
        return self.path2chain[path].invoke(data)


prompt = ChatPromptTemplate.from_template(get_response_template)
doc_chain = create_stuff_documents_chain(llm, prompt)

paths = [os.path.join('introduction', name) for name in os.listdir('train_Assessor/materials/introduction')]
paths = paths + [os.path.join('process', name) for name in os.listdir('train_Assessor/materials/process')]
# print(paths)

chains = ChainStore("train_Assessor/materials/", paths, doc_chain)


def get_response(path, chains, question, answer, base_path="train_Assessor/materials/"):
    response = chains.invoke(path, {"input": question})
    right_answer = response['answer']

    response = llm.invoke(score_template.format(question=question, answer=answer, right_answer=right_answer))


    print(f'right_answer={right_answer}\nresponse={response}')

    return right_answer, response


def get_recommendations(question: str, answer: str, lesson_slug: str) -> [int, str]:
    lesson = lesson_slug.split('_')[0]
    block = "_".join(lesson_slug.split('_')[1:])
    path = os.path.join(lesson, block + '.docx')
    right_answer, response = get_response(path, chains, question, answer)
    status = response.split('.')[0].lower() == 'да'
    text = '.'.join(response.split('.')[1:]).strip()
    return status, text
