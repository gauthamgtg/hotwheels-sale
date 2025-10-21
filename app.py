import streamlit as st
import pandas as pd
import requests
from typing import Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Hot Wheels Sale Tracker",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class GoogleSheetsCSV:
    """Handle Google Sheets data retrieval via CSV export"""
    
    def __init__(self):
        # Google Sheets CSV export URLs from Streamlit secrets
        self.sales_data_url = st.secrets["sales_data_url"]
        self.users_data_url = st.secrets["users_data_url"]
    
    def get_sales_data(self) -> Optional[pd.DataFrame]:
        """Get sales data from Google Sheets CSV"""
        try:
            response = requests.get(self.sales_data_url)
            response.raise_for_status()
            
            # Read CSV from string content
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            return df
        except Exception as e:
            st.error(f"Error fetching sales data: {str(e)}")
            return None
    
    def get_users_data(self) -> Optional[pd.DataFrame]:
        """Get users data from Google Sheets CSV"""
        try:
            response = requests.get(self.users_data_url)
            response.raise_for_status()
            
            # Read CSV from string content
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            return df
        except Exception as e:
            st.error(f"Error fetching users data: {str(e)}")
            return None

def authenticate_user(password: str, users_df: pd.DataFrame) -> Optional[str]:
    """Authenticate user and return their name if password matches"""
    if users_df is None:
        return None
        
    # Check for master password first
    master_password = st.secrets.get("master_pass")
    if password == master_password:
        return "MASTER_USER"
        
    # Find user with matching password
    matching_user = users_df[users_df['Password'] == password]
    if not matching_user.empty:
        return matching_user.iloc[0]['Name']
    return None

def filter_sales_data(sales_df: pd.DataFrame, user_name: str) -> pd.DataFrame:
    """Filter sales data for specific user"""
    if sales_df is None:
        return pd.DataFrame()
    
    # Return all data for master user
    if user_name == "MASTER_USER":
        return sales_df
    
    return sales_df[sales_df['Buyer'] == user_name]

def main():
    st.title("🏎️ Hot Wheels Purchase Tracker")
    st.markdown("---")
    
    # Customer login section in main area
    st.header("🔐 Customer Login")
    st.markdown("Enter your unique password to view your purchases")
    
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    # Refresh data button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Coming soon announcement
    st.markdown("---")
    st.info("🚀 **Coming Soon**: Euro Speed Sets, Mustangs, Corvettes, 1:43 scale cars and much more..!!")
    
    # Initialize Google Sheets CSV reader
    sheets_csv = GoogleSheetsCSV()
    
    if password:
        # Get data from sheets
        with st.spinner("Loading data..."):
            sales_df = sheets_csv.get_sales_data()
            users_df = sheets_csv.get_users_data()
        
        if sales_df is not None and users_df is not None:
            # Authenticate user
            user_name = authenticate_user(password, users_df)
            
            if user_name:
                if user_name == "MASTER_USER":
                    st.success("Welcome, Master User! 🎉")
                    st.info("🔑 **Master Access**: Viewing all sales data")
                else:
                    st.success(f"Welcome, {user_name}! 🎉")
                
                # Filter and display user's data
                user_sales = filter_sales_data(sales_df, user_name)
                
                if not user_sales.empty:
                    if user_name == "MASTER_USER":
                        st.subheader(f"All Sales Data ({len(user_sales)} items)")
                    else:
                        st.subheader(f"Your Purchases ({len(user_sales)} items)")
                    
                    # Calculate statistics
                    try:
                        price_values = pd.to_numeric(user_sales['Price'], errors='coerce')
                        total_value = price_values.sum()
                        
                        # Calculate paid and pending amounts
                        payment_status_str = user_sales['Payment Status'].astype(str)
                        paid_mask = payment_status_str.str.contains('paid', case=False, na=False)
                        pending_mask = ~paid_mask
                        
                        paid_amount = price_values[paid_mask].sum() if paid_mask.any() else 0
                        pending_amount = price_values[pending_mask].sum() if pending_mask.any() else 0
                        
                        paid_items = len(user_sales[paid_mask])
                        pending_items = len(user_sales[pending_mask])
                        
                    except:
                        total_value = 0
                        paid_amount = 0
                        pending_amount = 0
                        paid_items = 0
                        pending_items = 0
                    
                    # Summary statistics at the top
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if user_name == "MASTER_USER":
                            st.metric("Total Sales", len(user_sales))
                        else:
                            st.metric("Total Items", len(user_sales))
                    with col2:
                        if user_name == "MASTER_USER":
                            st.metric("Total Revenue", f"₹{total_value:,.0f}")
                        else:
                            st.metric("Total Spent", f"₹{total_value:,.0f}")
                    with col3:
                        if user_name == "MASTER_USER":
                            st.metric("Paid Orders", paid_items)
                        else:
                            st.metric("Paid Items", paid_items)
                    with col4:
                        if user_name == "MASTER_USER":
                            st.metric("Revenue Collected", f"₹{paid_amount:,.0f}")
                        else:
                            st.metric("Amount Paid", f"₹{paid_amount:,.0f}")
                    with col5:
                        if user_name == "MASTER_USER":
                            st.metric("Outstanding Amount", f"₹{pending_amount:,.0f}")
                        else:
                            st.metric("Amount Due", f"₹{pending_amount:,.0f}")
                    
                    st.markdown("---")
                    
                    # Note about car names
                    st.info("ℹ️ **Note**: The car names have been simplified for easier data entry. Please check the post for the accurate details of car and image.")
                    
                    # Display the data in a nice table with clickable links and images
                    st.dataframe(
                        user_sales,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Post Link": st.column_config.LinkColumn(
                                "Post Link",
                                help="Click to view the product listing",
                                display_text="View Listing"
                            ),
                            "Image address": st.column_config.ImageColumn(
                                "Image",
                                help="Product image"
                            )
                        }
                    )
                else:
                    st.info("No purchases found for your account.")
            else:
                st.error("❌ Invalid password. Please check your password and try again.")
                st.markdown("---")
                st.markdown("**For support and inquiries:**")
                st.markdown("**Gautham Mahadevan** 📱 [Facebook Profile](https://www.facebook.com/gloriousgautham/)")
                st.markdown("Contact for password issues or account setup")
        else:
            st.error("Failed to load data from Google Sheets. Please check your internet connection and try again.")
    
    else:
        st.info("👋 Welcome! Please enter your password above to view your purchases.")
        
        # Display contact information
        st.markdown("---")
        st.markdown("**For support and inquiries:**")
        st.markdown("**Gautham Mahadevan** 📱 [Facebook Profile](https://www.facebook.com/gloriousgautham/)")
        st.markdown("Contact for password issues or account setup")

if __name__ == "__main__":
    main()
