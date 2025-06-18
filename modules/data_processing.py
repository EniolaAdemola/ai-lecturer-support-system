#=======================Convert df into document==================

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter



def df_to_document(df):
    # First create documents from dataframe rows
    documents = [Document(page_content="\n".join(f"{col}: {row[col]}" for col in df.columns)) for _, row in df.iterrows()]
    
    # Then chunk them into smaller pieces for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", ",", " ", ""]
    )
    
    chunked_documents = text_splitter.split_documents(documents)
    return chunked_documents