import streamlit as st
import json
import os
from datetime import datetime


# full_hide = """
#     <style>
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}
#         header {visibility: hidden;}
#         a[href*="https://share.streamlit.io/user/"] {
#             display: none !important;
#         }
#         div[class^="_profileContainer"] {
#             display: none !important;
#         }
#     </style>
# """
# st.markdown(full_hide, unsafe_allow_html=True)


# Set page config
st.set_page_config(
    page_title="Chat History - AI LECTURER SUPPORT SYSTEM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication
if not st.session_state.get('authenticated', False):
    st.switch_page("pages/login.py")

# Chat history management functions
def load_chat_history_from_file():
    """Load chat history from file"""
    try:
        chat_dir = "chat_history"
        filename = f"{chat_dir}/{st.session_state.username}_chat_history.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return []

def save_chat_history_to_file(chat_history):
    """Save chat history to file"""
    try:
        chat_dir = "chat_history"
        if not os.path.exists(chat_dir):
            os.makedirs(chat_dir)
        
        filename = f"{chat_dir}/{st.session_state.username}_chat_history.json"
        with open(filename, 'w') as f:
            json.dump(chat_history, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")
        return False

def delete_chat_entry(index, chat_history):
    """Delete a specific chat entry"""
    if 0 <= index < len(chat_history):
        deleted_entry = chat_history.pop(index)
        if save_chat_history_to_file(chat_history):
            st.session_state.chat_history = chat_history
            return True
    return False

def export_chat_history(chat_history):
    """Export chat history as JSON"""
    try:
        export_data = {
            'user': st.session_state.username,
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_conversations': len(chat_history),
            'conversations': chat_history
        }
        return json.dumps(export_data, indent=2)
    except Exception as e:
        st.error(f"Error exporting chat history: {str(e)}")
        return None

# Load chat history
chat_history = load_chat_history_from_file()

# Sidebar navigation
with st.sidebar:
    st.write("### Navigation")
    
    if st.button("🏠 Back to Main", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # Chat statistics
    st.write("### 📊 Statistics")
    st.metric("Total Conversations", len(chat_history))
    
    if chat_history:
        # Date range
        dates = [datetime.strptime(chat['timestamp'], "%Y-%m-%d %H:%M:%S") for chat in chat_history]
        earliest = min(dates).strftime("%Y-%m-%d")
        latest = max(dates).strftime("%Y-%m-%d")
        
        st.write(f"**First Chat:** {earliest}")
        st.write(f"**Latest Chat:** {latest}")
    
    st.divider()
    
    # Actions
    st.write("### 🔧 Actions")
    
    # Export button
    if chat_history:
        export_data = export_chat_history(chat_history)
        if export_data:
            st.download_button(
                label="📥 Export Chat History",
                data=export_data,
                file_name=f"{st.session_state.username}_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Clear all button
    if chat_history:
        if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
            st.session_state.show_clear_confirm = True

# Handle clear confirmation
if st.session_state.get('show_clear_confirm', False):
    with st.sidebar:
        st.warning("⚠️ Are you sure you want to clear all chat history?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes", use_container_width=True):
                if save_chat_history_to_file([]):
                    st.session_state.chat_history = []
                    st.session_state.show_clear_confirm = False
                    st.success("All chat history cleared!")
                    st.rerun()
        with col2:
            if st.button("❌ No", use_container_width=True):
                st.session_state.show_clear_confirm = False
                st.rerun()

# Main content
st.title("💬 Chat History")
st.write(f"Viewing chat history for: **{st.session_state.username}**")

if not chat_history:
    st.info("📋 No chat history found. Start chatting in the main application to see your conversations here!")
    
    if st.button("🏠 Go to Main Application"):
        st.switch_page("app.py")
else:
    # Filter and search options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search conversations", placeholder="Search in questions or answers...")
    
    with col2:
        sort_order = st.selectbox("📅 Sort by", ["Newest First", "Oldest First"])
    
    with col3:
        items_per_page = st.selectbox("📄 Items per page", [10, 25, 50, 100])
    
    # Filter chat history based on search
    if search_term:
        filtered_history = [
            chat for chat in chat_history 
            if search_term.lower() in chat['question'].lower() or search_term.lower() in chat['answer'].lower()
        ]
    else:
        filtered_history = chat_history.copy()
    
    # Sort chat history
    if sort_order == "Newest First":
        filtered_history.reverse()
    
    # Pagination
    total_items = len(filtered_history)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    if total_items > items_per_page:
        page = st.selectbox(f"Page (1-{total_pages})", range(1, total_pages + 1))
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        page_history = filtered_history[start_idx:end_idx]
    else:
        page_history = filtered_history
        start_idx = 0
        end_idx = total_items
    
    # Display results info
    if search_term:
        st.write(f"Found **{total_items}** conversations matching '{search_term}'")
    
    if total_items > items_per_page:
        st.write(f"Showing {start_idx + 1}-{end_idx} of {total_items} conversations")
    
    st.divider()
    
    # Display chat history
    for i, chat in enumerate(page_history):
        original_index = chat_history.index(chat) if sort_order == "Oldest First" else len(chat_history) - 1 - chat_history.index(chat)
        
        with st.expander(f"💬 {chat['timestamp']} - {chat['question'][:100]}{'...' if len(chat['question']) > 100 else ''}", expanded=False):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**🤔 Question:**")
                st.write(chat['question'])
                
                st.markdown(f"**🤖 Answer:**")
                st.write(chat['answer'])
                
                st.markdown(f"**🕒 Timestamp:** {chat['timestamp']}")
            
            with col2:
                st.write("### Actions")
                
                # Copy question button
                if st.button(f"📋 Copy Q", key=f"copy_q_{i}"):
                    # Note: Streamlit doesn't have native clipboard support
                    # You could implement this with JavaScript if needed
                    st.info("Question copied to clipboard! (Note: Feature requires JavaScript implementation)")
                
                # Copy answer button
                if st.button(f"📋 Copy A", key=f"copy_a_{i}"):
                    st.info("Answer copied to clipboard! (Note: Feature requires JavaScript implementation)")
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{i}", type="secondary"):
                    if delete_chat_entry(original_index, chat_history):
                        st.success("Chat deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete chat")

# Footer
st.markdown("---")
st.markdown("*AI Lecturer Support System - Chat History Management*")