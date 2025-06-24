from dotenv import load_dotenv
import streamlit as st
import os
import hashlib
import json
from datetime import datetime
from modules.data_loader import load_excel_data
from modules.data_processing import df_to_document
from modules.vectorstore_handler import load_vectorstore, create_vectorstore
from modules.rag_chain import create_qa_chain

load_dotenv()




# Set page config
st.set_page_config(
    page_title="AI LECTURER SUPPORT SYSTEM",
    layout="wide",
    initial_sidebar_state="expanded"
)









# Initialize session state
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'file_hash' not in st.session_state:
        st.session_state.file_hash = None

initialize_session_state()

# Authentication check - redirect to login if not authenticated
if not st.session_state.authenticated:
    st.switch_page("pages/login.py")

# Chat history management functions
def save_chat_to_history(question, answer):
    """Save a chat exchange to history if it's not a duplicate"""
    chat_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'question': question,
        'answer': answer
    }
    
    # Check for duplicates before adding
    is_duplicate = False
    for existing_chat in st.session_state.chat_history:
        if existing_chat['question'] == question and existing_chat['answer'] == answer:
            is_duplicate = True
            break
    
    if not is_duplicate:
        st.session_state.chat_history.append(chat_entry)
        save_chat_history_to_file()
        return True
    return False

def save_chat_history_to_file():
    """Save chat history to a JSON file"""
    try:
        chat_dir = "chat_history"
        if not os.path.exists(chat_dir):
            os.makedirs(chat_dir)
        
        filename = f"{chat_dir}/{st.session_state.username}_chat_history.json"
        with open(filename, 'w') as f:
            json.dump(st.session_state.chat_history, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def load_chat_history_from_file():
    """Load chat history from file"""
    try:
        chat_dir = "chat_history"
        filename = f"{chat_dir}/{st.session_state.username}_chat_history.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                st.session_state.chat_history = json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")

def clear_chat_history():
    """Clear all chat history"""
    st.session_state.chat_history = []
    save_chat_history_to_file()

# Load chat history for current user
load_chat_history_from_file()

# Main app layout
st.title("AI LECTURER SUPPORT SYSTEM")
st.write(f"Welcome, {st.session_state.username}!")

# Sidebar for navigation and chat history
with st.sidebar:
    st.write("### Navigation")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.chat_history = []
        st.session_state.file_hash = None
        st.rerun()
    
    st.divider()
    
    # Chat history section
    st.write("### Chat History")
    
    if st.session_state.chat_history:
        # Clear history button
        if st.button("🗑️ Clear All Chats", use_container_width=True):
            clear_chat_history()
            st.success("Chat history cleared!")
            st.rerun()
        
        st.write(f"**Total conversations:** {len(st.session_state.chat_history)}")
        
        # Show recent chats (last 5)
        st.write("**Recent Chats:**")
        recent_chats = st.session_state.chat_history[-5:] if len(st.session_state.chat_history) > 5 else st.session_state.chat_history
        
        for i, chat in enumerate(reversed(recent_chats)):
            with st.expander(f"💬 {chat['timestamp']}", expanded=False):
                st.write(f"**Q:** {chat['question'][:100]}...")
                st.write(f"**A:** {chat['answer'][:200]}...")
    else:
        st.info("No chat history yet. Start asking questions!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Define data directory
    DATA_DIR = os.path.join(os.getcwd(), "data")

    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📤 Upload File", "📁 Use Existing File"])

    # Load or create vectorstore
    vectorstore = load_vectorstore()

    # Tab 1: File upload
    with tab1:
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "csv"])
        
        if uploaded_file:
            # Create data directory if it doesn't exist
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            
            # Save the uploaded file to data directory
            file_path = os.path.join(DATA_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the saved file
            with open(file_path, 'rb') as f:
                file_content = f.read()
                current_file_hash = hashlib.md5(file_content).hexdigest()
            
            create_new_vectorstore = False
            
            if vectorstore is None or st.session_state.file_hash != current_file_hash:
                create_new_vectorstore = True
                st.session_state.file_hash = current_file_hash
            
            st.success(f"✅ Excel file uploaded and saved to {file_path}!")
            df = load_excel_data(file_path)
            
            with st.expander("📊 Preview Data", expanded=False):
                st.dataframe(df)
            
            if create_new_vectorstore:
                with st.spinner("🔄 Processing and creating vectorstore..."):
                    documents = df_to_document(df)
                    vectorstore = create_vectorstore(documents)
                    st.success("✅ Vectorstore created and ready!")
            else:
                st.info("ℹ️ Vectorstore already exists for this file.")

    # Tab 2: Use existing file from data directory
    with tab2:
        # Check if data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            st.info(f"📁 Data directory created at {DATA_DIR}. Please add files to this directory.")
        
        # List files in data directory
        data_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls'))]
        
        if not data_files:
            st.info(f"📋 No Excel or CSV files found in {DATA_DIR}. Please add files to this directory.")
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
                
                st.success(f"✅ Using file: {selected_file}")
                df = load_excel_data(file_path)
                
                with st.expander("📊 Preview Data", expanded=False):
                    st.dataframe(df)
                
                if create_new_vectorstore:
                    with st.spinner("🔄 Processing and creating vectorstore..."):
                        documents = df_to_document(df)
                        vectorstore = create_vectorstore(documents)
                        st.success("✅ Vectorstore created and ready!")
                else:
                    st.info("ℹ️ Vectorstore already exists for this file.")

with col2:
    # Chat statistics
    if st.session_state.chat_history:
        st.write("### 📊 Chat Statistics")
        st.metric("Total Questions", len(st.session_state.chat_history))
        
        # Most recent chat time
        if st.session_state.chat_history:
            latest_chat = st.session_state.chat_history[-1]['timestamp']
            st.write(f"**Last Activity:** {latest_chat}")

# Question answering section
if vectorstore:
    st.markdown("---")
    st.subheader("💬 Ask Questions About Your Data")
    
    # Create columns for the input and button
    query_col, button_col = st.columns([4, 1])
    
    with query_col:
        query = st.text_input("Enter your question:", placeholder="What would you like to know about your data?")
    
    with button_col:
        ask_button = st.button("🚀 Ask", use_container_width=True)
    
    # Process query
    # Update the question answering section to handle duplicate detection
    if (query and ask_button) or (query and st.session_state.get('enter_pressed', True)):
        with st.spinner("🤔 Getting answer..."):
            try:
                qa_chain = create_qa_chain(vectorstore)
                response = qa_chain.invoke({"input": query})
                answer = response["answer"]
                
                # Display answer
                st.write("### 💡 Answer:")
                st.write(answer)
                
                # Save to chat history and check if it was a duplicate
                if save_chat_to_history(query, answer):
                    st.success("✅ Answer saved to chat history!")
                else:
                    st.info("ℹ️ This Q&A is already in your chat history.")
                
            except Exception as e:
                st.error(f"❌ Error getting answer: {str(e)}")
    
    # Display recent chat history in main area
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📝 Recent Conversations")
        
        # Show last 3 conversations
        recent_conversations = st.session_state.chat_history[-3:]
        
        for i, chat in enumerate(reversed(recent_conversations)):
            with st.expander(f"💬 {chat['timestamp']} - {chat['question'][:50]}...", expanded=i==0):
                st.write(f"**Question:** {chat['question']}")
                st.write(f"**Answer:** {chat['answer']}")
                st.write(f"**Time:** {chat['timestamp']}")

else:
    st.info("📋 Please upload or select an Excel file to start asking questions.")
    
# Footer
st.markdown("---")
st.markdown("*AI Lecturer Support System - Powered by RAG Technology*")