#================================Handle retrieval and generation chain================================



from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

def create_qa_chain(vectorstore):
    """Create a QA chain using create_retrieval_chain"""
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k":3}
    )
    llm = ChatGroq(model="gemma2-9b-it", temperature=0)
    
    system_prompt = (
        "Use the given context to answer the question. "
        "If you don't know the answer, say you don't know. "
        "Use three sentence maximum and keep the answer concise. "
        "Do not generate inacurrate answers"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return chain