from dotenv import load_dotenv
import streamlit as st
import os
import hashlib
from modules.data_loader import load_excel_data
from modules.data_processing import df_to_document
from modules.vectorstore_handler import load_vectorstore, create_vectorstore
from modules.rag_chain import create_qa_chain

load_dotenv()

st.set_page_config(page_title="Excel RAG", layout="wide")

st.title("AI LECTURER SUPPORT SYSTEM")

# Initialize session state for file hash
if 'file_hash' not in st.session_state:
    st.session_state.file_hash = None

# Define data directory
DATA_DIR = os.path.join(os.getcwd(), "data")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload File", "Use Existing File"])

# Load or create vectorstore
vectorstore = load_vectorstore()

# Tab 1: File upload
with tab1:
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "csv"])
    
    if uploaded_file:
        file_content = uploaded_file.read()
        current_file_hash = hashlib.md5(file_content).hexdigest()
        
        uploaded_file.seek(0)
        
        create_new_vectorstore = False
        
        if vectorstore is None or st.session_state.file_hash != current_file_hash:
            create_new_vectorstore = True
            st.session_state.file_hash = current_file_hash
        
        st.success("Excel file uploaded.")
        df = load_excel_data(uploaded_file)
        st.dataframe(df)
        
        if create_new_vectorstore:
            with st.spinner("Processing and creating vectorstore..."):
                documents = df_to_document(df)
                vectorstore = create_vectorstore(documents)
                st.success("Vectorstore saved and ready!")
        else:
            st.info("Vectorstore already exists. No need to create a new one.")

# Tab 2: Use existing file from data directory
with tab2:
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        st.info(f"Data directory created at {DATA_DIR}. Please add files to this directory.")
    
    # List files in data directory
    data_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not data_files:
        st.info(f"No Excel or CSV files found in {DATA_DIR}. Please add files to this directory.")
    else:
        selected_file = st.selectbox("Select a file from data directory", data_files)
        
        if selected_file:
            file_path = os.path.join(DATA_DIR, selected_file)
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_content = f.read()
                current_file_hash = hashlib.md5(file_content).hexdigest()
            
            create_new_vectorstore = False
            
            if vectorstore is None or st.session_state.file_hash != current_file_hash:
                create_new_vectorstore = True
                st.session_state.file_hash = current_file_hash
            
            st.success(f"Using file: {selected_file}")
            df = load_excel_data(file_path)
            st.dataframe(df)
            
            if create_new_vectorstore:
                with st.spinner("Processing and creating vectorstore..."):
                    documents = df_to_document(df)
                    vectorstore = create_vectorstore(documents)
                    st.success("Vectorstore saved and ready!")
            else:
                st.info("Vectorstore already exists. No need to create a new one.")

# Question answering section (common to both tabs)
if vectorstore:
    qa_chain = create_qa_chain(vectorstore)
    st.markdown("---")
    st.subheader("Ask Questions About Your Data")
    query = st.text_input("Enter your question:")
    if query:
        with st.spinner("Getting answer..."):
            response = qa_chain.invoke({"input": query})
            st.write("### Answer:")
            st.write(response["answer"])
else:
    st.info("Please upload or select an Excel file to start.")