"""
Judge.me Shopify App Store Ads Analysis Dashboard
Period: August 21, 2025 - February 18, 2026
Focus: Keyword Discovery for Install Growth
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_auth():
    """Check if user is authenticated"""

    # Check session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None

    if st.session_state.authenticated:
        return True

    # Show login page
    st.title("🔒 Judge.me Ads Dashboard")
    st.markdown("### Team Login")
    st.markdown("Enter the team password to access the dashboard.")

    password = st.text_input("Password:", type="password", key="login_password")

    if st.button("Login", type="primary"):
        # Get password from secrets, fallback to default
        correct_password = st.secrets.get("app_password", "judgeme2026")

        if password == correct_password:
            st.session_state.authenticated = True
            st.session_state.user_email = "team@judge.me"
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    st.markdown("---")
    st.caption("Contact your team admin for access.")
    return False


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Judge.me Ads Analysis",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .highlight-green { color: #28a745; font-weight: bold; }
    .highlight-red { color: #dc3545; font-weight: bold; }
    .highlight-yellow { color: #ffc107; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; }
    .upload-section {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def get_default_campaign_data():
    """Return default campaign summary data"""
    return pd.DataFrame({
        'Campaign': [
            'Search_EN_ProductReview_2024.08.05',
            'Search_EN_Competitors_2024.08.12',
            'Search_EN_Review-variations_2024.04.29',
            'Search_EN_Features_2024.08.19'
        ],
        'Total Spend': [43736.3, 5664.5, 6501.34, 14780.0],
        'Total Installs': [13539, 1330, 1180, 2127],
        'Avg CPI': [3.23, 4.26, 5.51, 6.95],
        'Avg Install Rate': [0.72, 0.68, 0.64, 0.58],
        'Total Customers': [358, 67, 27, 46],
        'Total Revenue': [12152.57, 3467.45, 1117.55, 1629.19],
        'ROAS': [27.8, 61.2, 17.2, 11.0]
    })

def get_default_keywords_product_review():
    """Return default ProductReview keywords data"""
    return pd.DataFrame([
        {'Keyword': 'reviews', 'Match': 'exact', 'Bid': 2.1, 'Impressions': 36878, 'Clicks': 6348, 'Installs': 4594, 'Spend': 13848.8, 'CPI': 3.01, 'InstallRate': 0.72, 'ROAS': 30.2},
        {'Keyword': 'review', 'Match': 'exact', 'Bid': 1.5, 'Impressions': 23151, 'Clicks': 4101, 'Installs': 3201, 'Spend': 6151.5, 'CPI': 1.92, 'InstallRate': 0.78, 'ROAS': 37.7},
        {'Keyword': 'product review', 'Match': 'broad', 'Bid': 3.0, 'Impressions': 15329, 'Clicks': 2622, 'Installs': 2033, 'Spend': 7866.0, 'CPI': 3.87, 'InstallRate': 0.78, 'ROAS': 24.2},
        {'Keyword': 'product reviews', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 8614, 'Clicks': 1567, 'Installs': 1244, 'Spend': 4701.0, 'CPI': 3.78, 'InstallRate': 0.79, 'ROAS': 25.7},
        {'Keyword': 'google reviews', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 7848, 'Clicks': 652, 'Installs': 307, 'Spend': 3260.0, 'CPI': 10.62, 'InstallRate': 0.47, 'ROAS': 27.3},
        {'Keyword': 'product review', 'Match': 'exact', 'Bid': 2.5, 'Impressions': 4694, 'Clicks': 866, 'Installs': 685, 'Spend': 2165.0, 'CPI': 3.16, 'InstallRate': 0.79, 'ROAS': 21.0},
        {'Keyword': 'google review', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 3985, 'Clicks': 372, 'Installs': 180, 'Spend': 1860.0, 'CPI': 10.33, 'InstallRate': 0.48, 'ROAS': 28.6},
        {'Keyword': 'reviews app', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 2372, 'Clicks': 445, 'Installs': 336, 'Spend': 890.0, 'CPI': 2.65, 'InstallRate': 0.76, 'ROAS': 41.0},
        {'Keyword': 'shopify product reviews', 'Match': 'exact', 'Bid': 1.0, 'Impressions': 1876, 'Clicks': 392, 'Installs': 339, 'Spend': 392.0, 'CPI': 1.16, 'InstallRate': 0.86, 'ROAS': 50.3},
        {'Keyword': 'reviews free', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 1822, 'Clicks': 483, 'Installs': 374, 'Spend': 966.0, 'CPI': 2.58, 'InstallRate': 0.77, 'ROAS': 7.8},
        {'Keyword': 'review widget', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 973, 'Clicks': 242, 'Installs': 150, 'Spend': 1210.0, 'CPI': 8.07, 'InstallRate': 0.62, 'ROAS': 18.8},
        {'Keyword': 'customer reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 474, 'Clicks': 87, 'Installs': 72, 'Spend': 174.0, 'CPI': 2.42, 'InstallRate': 0.83, 'ROAS': 60.6},
        {'Keyword': 'video reviews', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 61, 'Clicks': 8, 'Installs': 5, 'Spend': 40.0, 'CPI': 8.0, 'InstallRate': 0.63, 'ROAS': 0},
        {'Keyword': 'photo reviews', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 20, 'Clicks': 2, 'Installs': 2, 'Spend': 10.0, 'CPI': 5.0, 'InstallRate': 1.0, 'ROAS': 0},
        {'Keyword': 'store reviews', 'Match': 'exact', 'Bid': 8.0, 'Impressions': 16, 'Clicks': 1, 'Installs': 1, 'Spend': 8.0, 'CPI': 8.0, 'InstallRate': 1.0, 'ROAS': 0},
    ])

def get_default_keywords_competitors():
    """Return default Competitors keywords data"""
    return pd.DataFrame([
        {'Keyword': 'loox', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 16543, 'Clicks': 785, 'Installs': 561, 'Spend': 2355.0, 'CPI': 4.20, 'InstallRate': 0.71, 'ROAS': 55.2, 'Customers': 30},
        {'Keyword': 'trustoo', 'Match': 'exact', 'Bid': 2.5, 'Impressions': 12689, 'Clicks': 244, 'Installs': 171, 'Spend': 610.0, 'CPI': 3.57, 'InstallRate': 0.70, 'ROAS': 17.5, 'Customers': 2},
        {'Keyword': 'trustpilot', 'Match': 'exact', 'Bid': 2.5, 'Impressions': 7806, 'Clicks': 488, 'Installs': 240, 'Spend': 1220.0, 'CPI': 5.08, 'InstallRate': 0.49, 'ROAS': 49.6, 'Customers': 13},
        {'Keyword': 'trustoo.io reviews', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 4876, 'Clicks': 70, 'Installs': 44, 'Spend': 210.0, 'CPI': 4.77, 'InstallRate': 0.63, 'ROAS': 0, 'Customers': 0},
        {'Keyword': 'loox', 'Match': 'broad', 'Bid': 3.5, 'Impressions': 3519, 'Clicks': 153, 'Installs': 109, 'Spend': 535.5, 'CPI': 4.91, 'InstallRate': 0.71, 'ROAS': 28.3, 'Customers': 5},
        {'Keyword': 'loox review', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 2477, 'Clicks': 120, 'Installs': 83, 'Spend': 240.0, 'CPI': 2.89, 'InstallRate': 0.69, 'ROAS': 76.1, 'Customers': 5},
        {'Keyword': 'okendo', 'Match': 'exact', 'Bid': 3.5, 'Impressions': 2041, 'Clicks': 74, 'Installs': 35, 'Spend': 259.0, 'CPI': 7.40, 'InstallRate': 0.47, 'ROAS': 151.5, 'Customers': 9},
        {'Keyword': 'trustoo reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 1164, 'Clicks': 21, 'Installs': 17, 'Spend': 42.0, 'CPI': 2.47, 'InstallRate': 0.81, 'ROAS': 0, 'Customers': 0},
        {'Keyword': 'rivo reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 692, 'Clicks': 35, 'Installs': 26, 'Spend': 70.0, 'CPI': 2.69, 'InstallRate': 0.74, 'ROAS': 0, 'Customers': 0},
        {'Keyword': 'yotpo reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 554, 'Clicks': 11, 'Installs': 7, 'Spend': 22.0, 'CPI': 3.14, 'InstallRate': 0.64, 'ROAS': 341.0, 'Customers': 1},
        {'Keyword': 'klaviyo reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 411, 'Clicks': 13, 'Installs': 9, 'Spend': 26.0, 'CPI': 2.89, 'InstallRate': 0.69, 'ROAS': 0, 'Customers': 0},
        {'Keyword': 'loox - photo reviews', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 360, 'Clicks': 20, 'Installs': 17, 'Spend': 40.0, 'CPI': 2.35, 'InstallRate': 0.85, 'ROAS': 190.4, 'Customers': 2},
        {'Keyword': 'reviews io', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 96, 'Clicks': 3, 'Installs': 3, 'Spend': 6.0, 'CPI': 2.0, 'InstallRate': 1.0, 'ROAS': 0, 'Customers': 0},
        {'Keyword': 'tydal review', 'Match': 'exact', 'Bid': 2.0, 'Impressions': 37, 'Clicks': 3, 'Installs': 2, 'Spend': 6.0, 'CPI': 3.0, 'InstallRate': 0.67, 'ROAS': 0, 'Customers': 0},
    ])

def get_default_keywords_review_variations():
    """Return default Review-variations keywords data"""
    return pd.DataFrame([
        {'Keyword': 'testimonial', 'Match': 'broad', 'Bid': 2.5, 'Impressions': 6402, 'Clicks': 784, 'Installs': 474, 'Spend': 1960.0, 'CPI': 4.14, 'InstallRate': 0.60, 'ROAS': 13.8},
        {'Keyword': 'product rating', 'Match': 'broad', 'Bid': 4.5, 'Impressions': 5924, 'Clicks': 270, 'Installs': 185, 'Spend': 1215.0, 'CPI': 6.57, 'InstallRate': 0.69, 'ROAS': 24.9},
        {'Keyword': 'customer feedback', 'Match': 'broad', 'Bid': 5.0, 'Impressions': 5425, 'Clicks': 320, 'Installs': 185, 'Spend': 1600.0, 'CPI': 8.65, 'InstallRate': 0.58, 'ROAS': 9.5},
        {'Keyword': 'testimonial', 'Match': 'exact', 'Bid': 2.82, 'Impressions': 2714, 'Clicks': 337, 'Installs': 202, 'Spend': 950.34, 'CPI': 4.70, 'InstallRate': 0.60, 'ROAS': 23.9},
        {'Keyword': 'product rating', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 490, 'Clicks': 42, 'Installs': 28, 'Spend': 126.0, 'CPI': 4.50, 'InstallRate': 0.67, 'ROAS': 0},
        {'Keyword': 'feedback app', 'Match': 'broad', 'Bid': 3.0, 'Impressions': 415, 'Clicks': 10, 'Installs': 4, 'Spend': 30.0, 'CPI': 7.50, 'InstallRate': 0.40, 'ROAS': 0},
        {'Keyword': 'ratings', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 342, 'Clicks': 124, 'Installs': 102, 'Spend': 620.0, 'CPI': 6.08, 'InstallRate': 0.82, 'ROAS': 26.6},
    ])

def get_default_keywords_features():
    """Return default Features keywords data"""
    return pd.DataFrame([
        {'Keyword': 'amazon reviews importer', 'Match': 'broad', 'Bid': 5.0, 'Impressions': 23541, 'Clicks': 1877, 'Installs': 1356, 'Spend': 9385.0, 'CPI': 6.92, 'InstallRate': 0.72, 'ROAS': 12.5},
        {'Keyword': 'etsy importer', 'Match': 'broad', 'Bid': 5.0, 'Impressions': 9028, 'Clicks': 412, 'Installs': 268, 'Spend': 2060.0, 'CPI': 7.69, 'InstallRate': 0.65, 'ROAS': 13.9},
        {'Keyword': 'carousel', 'Match': 'broad', 'Bid': 6.0, 'Impressions': 4786, 'Clicks': 116, 'Installs': 41, 'Spend': 696.0, 'CPI': 16.98, 'InstallRate': 0.35, 'ROAS': 2.2},
        {'Keyword': 'ugc', 'Match': 'broad', 'Bid': 7.0, 'Impressions': 2676, 'Clicks': 81, 'Installs': 31, 'Spend': 567.0, 'CPI': 18.29, 'InstallRate': 0.38, 'ROAS': 0},
        {'Keyword': 'amazon reviews', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 1655, 'Clicks': 148, 'Installs': 93, 'Spend': 444.0, 'CPI': 4.77, 'InstallRate': 0.63, 'ROAS': 3.4},
        {'Keyword': 'review importer', 'Match': 'exact', 'Bid': 3.6, 'Impressions': 1430, 'Clicks': 192, 'Installs': 147, 'Spend': 691.2, 'CPI': 4.70, 'InstallRate': 0.77, 'ROAS': 4.3},
        {'Keyword': 'reviews importer', 'Match': 'exact', 'Bid': 3.2, 'Impressions': 1409, 'Clicks': 239, 'Installs': 176, 'Spend': 764.8, 'CPI': 4.35, 'InstallRate': 0.74, 'ROAS': 13.8},
        {'Keyword': 'rich snippet', 'Match': 'broad', 'Bid': 5.0, 'Impressions': 605, 'Clicks': 12, 'Installs': 7, 'Spend': 60.0, 'CPI': 8.57, 'InstallRate': 0.58, 'ROAS': 0},
        {'Keyword': 'q&a', 'Match': 'broad', 'Bid': 6.0, 'Impressions': 506, 'Clicks': 12, 'Installs': 4, 'Spend': 72.0, 'CPI': 18.0, 'InstallRate': 0.33, 'ROAS': 0},
        {'Keyword': 'coupons', 'Match': 'broad', 'Bid': 2.0, 'Impressions': 389, 'Clicks': 6, 'Installs': 2, 'Spend': 12.0, 'CPI': 6.0, 'InstallRate': 0.33, 'ROAS': 0},
    ])

def get_default_new_keywords():
    """Return default new keyword recommendations"""
    return pd.DataFrame([
        {'Keyword': 'testimonials', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 3500, 'Est. Installs': 280, 'Rationale': 'High volume search term with 321 installs via broad match'},
        {'Keyword': 'testimonial slider', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 1500, 'Est. Installs': 100, 'Rationale': '127 installs from broad match, specific feature intent'},
        {'Keyword': 'rating', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 4.00, 'Est. Impressions': 1500, 'Est. Installs': 120, 'Rationale': '146 installs, 77% install rate - strong performer'},
        {'Keyword': 'loox reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.50, 'Est. Impressions': 3000, 'Est. Installs': 95, 'Rationale': 'Competitor comparison intent, 100 installs via broad'},
        {'Keyword': 'star rating', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.50, 'Est. Impressions': 800, 'Est. Installs': 60, 'Rationale': 'Core feature term, high relevance'},
        {'Keyword': 'stamped.io', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 2000, 'Est. Installs': 80, 'Rationale': 'Major competitor not yet targeted'},
        {'Keyword': 'stamped reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 1200, 'Est. Installs': 50, 'Rationale': 'Competitor + reviews intent'},
        {'Keyword': 'fera reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 800, 'Est. Installs': 35, 'Rationale': 'Growing competitor, untapped'},
        {'Keyword': 'vitals reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 500, 'Est. Installs': 25, 'Rationale': 'Vitals app users seeking reviews'},
        {'Keyword': 'growave reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 400, 'Est. Installs': 20, 'Rationale': 'Multi-feature competitor'},
        {'Keyword': 'photo review app', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 500, 'Est. Installs': 40, 'Rationale': 'Feature-specific, high intent'},
        {'Keyword': 'video review app', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 400, 'Est. Installs': 30, 'Rationale': 'Video reviews feature intent'},
        {'Keyword': 'review request email', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 600, 'Est. Installs': 45, 'Rationale': 'Core feature, automation intent'},
        {'Keyword': 'google shopping reviews', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 800, 'Est. Installs': 50, 'Rationale': 'SEO/Rich snippet intent'},
        {'Keyword': 'aliexpress reviews', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 1200, 'Est. Installs': 80, 'Rationale': 'Import feature, dropship audience'},
        {'Keyword': 'ebay reviews importer', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 400, 'Est. Installs': 25, 'Rationale': 'Import feature expansion'},
        {'Keyword': 'review carousel', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 500, 'Est. Installs': 35, 'Rationale': 'Display feature intent'},
        {'Keyword': 'review widget', 'Match Type': 'broad', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 800, 'Est. Installs': 50, 'Rationale': 'Expand widget coverage'},
        {'Keyword': 'dropshipping reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 600, 'Est. Installs': 40, 'Rationale': 'Target dropship segment'},
        {'Keyword': 'shopify store reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 2.50, 'Est. Impressions': 1000, 'Est. Installs': 70, 'Rationale': 'Platform-specific intent'},
        {'Keyword': 'ecommerce reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 3.00, 'Est. Impressions': 500, 'Est. Installs': 35, 'Rationale': 'Broad ecommerce audience'},
        {'Keyword': 'social proof', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'LOW', 'Suggested Bid': 3.00, 'Est. Impressions': 400, 'Est. Installs': 20, 'Rationale': 'Conceptual term, test performance'},
        {'Keyword': 'trust badges', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'LOW', 'Suggested Bid': 2.50, 'Est. Impressions': 500, 'Est. Installs': 25, 'Rationale': 'Related concept, may convert'},
        {'Keyword': 'nps survey', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'LOW', 'Suggested Bid': 3.00, 'Est. Impressions': 300, 'Est. Installs': 15, 'Rationale': 'NPS feature awareness'},
        {'Keyword': 'review syndication', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'LOW', 'Suggested Bid': 4.00, 'Est. Impressions': 200, 'Est. Installs': 15, 'Rationale': 'Enterprise feature'},
    ])

def get_default_keywords_to_pause():
    """Return default keywords to pause"""
    return pd.DataFrame([
        {'Keyword': 'customer feedback', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'PAUSE', 'Reason': 'High CPI ($8.65), low ROAS (9.5%), catching irrelevant searches', 'Spend': 1600.0, 'Installs': 185},
        {'Keyword': 'feedback app', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'PAUSE', 'Reason': 'Very low relevance - catching "free apps", "mobile app builder"', 'Spend': 30.0, 'Installs': 4},
        {'Keyword': 'product rating', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'REDUCE BID', 'Reason': 'Catching shipping rate searches. Reduce bid to $3.00', 'Spend': 1215.0, 'Installs': 185},
        {'Keyword': 'carousel', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'REDUCE BID', 'Reason': 'Very high CPI ($16.98). Reduce bid to $3.00', 'Spend': 696.0, 'Installs': 41},
        {'Keyword': 'ugc', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'REDUCE BID', 'Reason': 'Highest CPI ($18.29). Reduce bid to $4.00 or pause', 'Spend': 567.0, 'Installs': 31},
        {'Keyword': 'google reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Action': 'REDUCE BID', 'Reason': 'High CPI ($10.62). Reduce to $3.50', 'Spend': 3260.0, 'Installs': 307},
        {'Keyword': 'google review', 'Match': 'exact', 'Campaign': 'ProductReview', 'Action': 'REDUCE BID', 'Reason': 'High CPI ($10.33). Reduce to $3.50', 'Spend': 1860.0, 'Installs': 180},
        {'Keyword': 'q&a', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'PAUSE', 'Reason': 'Very high CPI ($18.00), low install rate (33%)', 'Spend': 72.0, 'Installs': 4},
    ])

def get_default_bid_increases():
    """Return default bid increase recommendations"""
    return pd.DataFrame([
        {'Keyword': 'okendo', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 3.50, 'Recommended Bid': 5.00, 'Reason': 'Highest ROAS (151.5%), best performer'},
        {'Keyword': 'yotpo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.50, 'Reason': 'Exceptional ROAS (341%)'},
        {'Keyword': 'loox - photo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 190.4%, install rate 85%'},
        {'Keyword': 'loox review', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 76.1%, good volume'},
        {'Keyword': 'shopify product reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 1.00, 'Recommended Bid': 2.00, 'Reason': 'Best CPI ($1.16), 86% install rate'},
        {'Keyword': 'customer reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 60.6%, install rate 83%'},
        {'Keyword': 'reviews app', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 41%, install rate 76%'},
        {'Keyword': 'review', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 1.50, 'Recommended Bid': 2.00, 'Reason': 'Best CPI ($1.92), 78% install rate'},
        {'Keyword': 'trustoo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'Excellent CPI ($2.47), 81% install rate'},
        {'Keyword': 'rivo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'Good CPI ($2.69), 74% install rate'},
        {'Keyword': 'reviews importer', 'Match': 'exact', 'Campaign': 'Features', 'Current Bid': 3.20, 'Recommended Bid': 4.00, 'Reason': 'Good CPI ($4.35), 74% install rate'},
        {'Keyword': 'review importer', 'Match': 'exact', 'Campaign': 'Features', 'Current Bid': 3.60, 'Recommended Bid': 4.50, 'Reason': 'Good volume, 77% install rate'},
    ])

def get_default_search_opportunities():
    """Return default search term opportunities"""
    return pd.DataFrame([
        {'Search Term': 'testimonials', 'Triggered By': 'testimonial (broad)', 'Impressions': 3748, 'Clicks': 517, 'Installs': 321, 'Spend': 1292.5, 'CPI': 4.03, 'InstallRate': 0.62, 'Recommendation': 'Add as exact match', 'Suggested Bid': 3.0},
        {'Search Term': 'testimonial slider', 'Triggered By': 'testimonial (broad)', 'Impressions': 1752, 'Clicks': 219, 'Installs': 127, 'Spend': 547.5, 'CPI': 4.31, 'InstallRate': 0.58, 'Recommendation': 'Add as exact match', 'Suggested Bid': 3.0},
        {'Search Term': 'rating', 'Triggered By': 'product rating (broad)', 'Impressions': 1675, 'Clicks': 189, 'Installs': 146, 'Spend': 850.5, 'CPI': 5.83, 'InstallRate': 0.77, 'Recommendation': 'Add as exact match', 'Suggested Bid': 4.0},
        {'Search Term': 'feedback', 'Triggered By': 'customer feedback (broad)', 'Impressions': 1077, 'Clicks': 241, 'Installs': 156, 'Spend': 1205.0, 'CPI': 7.72, 'InstallRate': 0.65, 'Recommendation': 'Consider - high CPI', 'Suggested Bid': 3.5},
        {'Search Term': 'loox reviews', 'Triggered By': 'loox (broad)', 'Impressions': 3216, 'Clicks': 140, 'Installs': 100, 'Spend': 490.0, 'CPI': 4.90, 'InstallRate': 0.71, 'Recommendation': 'Add as exact match', 'Suggested Bid': 3.5},
        {'Search Term': 'testimony', 'Triggered By': 'testimonial (broad)', 'Impressions': 42, 'Clicks': 9, 'Installs': 5, 'Spend': 22.5, 'CPI': 4.50, 'InstallRate': 0.56, 'Recommendation': 'Add as exact match', 'Suggested Bid': 2.5},
        {'Search Term': 'rating app', 'Triggered By': 'product rating (broad)', 'Impressions': 21, 'Clicks': 3, 'Installs': 2, 'Spend': 13.5, 'CPI': 6.75, 'InstallRate': 0.67, 'Recommendation': 'Add as exact match', 'Suggested Bid': 3.5},
        {'Search Term': 'feedbacks', 'Triggered By': 'customer feedback (broad)', 'Impressions': 27, 'Clicks': 5, 'Installs': 3, 'Spend': 25.0, 'CPI': 8.33, 'InstallRate': 0.60, 'Recommendation': 'Add as exact match', 'Suggested Bid': 3.0},
        {'Search Term': 'rate me', 'Triggered By': 'product rating (broad)', 'Impressions': 8, 'Clicks': 5, 'Installs': 3, 'Spend': 22.5, 'CPI': 7.50, 'InstallRate': 0.60, 'Recommendation': 'Add as exact match', 'Suggested Bid': 4.0},
        {'Search Term': 'testimonial showcase', 'Triggered By': 'testimonial (broad)', 'Impressions': 6, 'Clicks': 1, 'Installs': 1, 'Spend': 2.5, 'CPI': 2.50, 'InstallRate': 1.0, 'Recommendation': 'Add as exact match', 'Suggested Bid': 2.5},
    ])


def load_data():
    """Load data from session state or defaults"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = True
        st.session_state.df_campaigns = get_default_campaign_data()
        st.session_state.df_kw_product_review = get_default_keywords_product_review()
        st.session_state.df_kw_competitors = get_default_keywords_competitors()
        st.session_state.df_kw_review_variations = get_default_keywords_review_variations()
        st.session_state.df_kw_features = get_default_keywords_features()
        st.session_state.df_new_keywords = get_default_new_keywords()
        st.session_state.df_keywords_to_pause = get_default_keywords_to_pause()
        st.session_state.df_bid_increases = get_default_bid_increases()
        st.session_state.df_search_opportunities = get_default_search_opportunities()
        st.session_state.data_period = "Aug 21, 2025 - Feb 18, 2026"


def process_keywords_upload(uploaded_file, campaign_name):
    """Process uploaded keywords CSV file"""
    try:
        df = pd.read_csv(uploaded_file)

        # Expected columns from Shopify export
        column_mapping = {
            'Keyword': 'Keyword',
            'Match Type': 'Match',
            'Bid': 'Bid',
            'Impressions': 'Impressions',
            'Clicks': 'Clicks',
            'Installs': 'Installs',
            'Spend': 'Spend',
            'Cost Per Install': 'CPI',
            'Install Rate': 'InstallRate',
            'Return On Spend': 'ROAS'
        }

        # Rename columns if they exist
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        # Calculate CPI if not present
        if 'CPI' not in df.columns and 'Spend' in df.columns and 'Installs' in df.columns:
            df['CPI'] = df.apply(lambda x: x['Spend'] / x['Installs'] if x['Installs'] > 0 else 0, axis=1)

        return df, None
    except Exception as e:
        return None, str(e)


def process_campaign_metrics_upload(uploaded_file):
    """Process uploaded campaign metrics CSV file"""
    try:
        df = pd.read_csv(uploaded_file)

        # Aggregate by campaign/ad name
        if 'Ad Name' in df.columns:
            agg_df = df.groupby('Ad Name').agg({
                'Spend': 'sum',
                'Installs': 'sum',
                'Customers': 'sum',
                'Revenue': 'sum',
                'Clicks': 'sum',
                'Impressions': 'sum'
            }).reset_index()

            agg_df['Campaign'] = agg_df['Ad Name']
            agg_df['Total Spend'] = agg_df['Spend']
            agg_df['Total Installs'] = agg_df['Installs']
            agg_df['Avg CPI'] = agg_df.apply(lambda x: x['Spend'] / x['Installs'] if x['Installs'] > 0 else 0, axis=1)
            agg_df['Avg Install Rate'] = agg_df.apply(lambda x: x['Installs'] / x['Clicks'] if x['Clicks'] > 0 else 0, axis=1)
            agg_df['Total Customers'] = agg_df['Customers']
            agg_df['Total Revenue'] = agg_df['Revenue']
            agg_df['ROAS'] = agg_df.apply(lambda x: (x['Revenue'] / x['Spend'] * 100) if x['Spend'] > 0 else 0, axis=1)

            return agg_df[['Campaign', 'Total Spend', 'Total Installs', 'Avg CPI', 'Avg Install Rate', 'Total Customers', 'Total Revenue', 'ROAS']], None

        return None, "Missing 'Ad Name' column"
    except Exception as e:
        return None, str(e)


# ============================================================================
# MAIN APP
# ============================================================================

# Load data
load_data()

# Check authentication
if not check_auth():
    st.stop()

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("Judge.me Ads Dashboard")

# User info (if authenticated)
if st.session_state.get('user_email'):
    st.sidebar.markdown(f"👤 {st.session_state.user_email}")
    st.sidebar.markdown("---")

st.sidebar.markdown("**Navigation**")

page = st.sidebar.radio(
    "Select Section:",
    ["Executive Summary", "Campaign Performance", "Keyword Analysis",
     "New Keywords", "Keywords to Pause", "Bid Recommendations",
     "Search Term Opportunities", "Negative Keywords", "Action Checklist",
     "📤 Upload Data"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data Period:**")
st.sidebar.markdown(st.session_state.get('data_period', 'Aug 21, 2025 - Feb 18, 2026'))
st.sidebar.markdown("**Focus:**")
st.sidebar.markdown("Keyword Discovery for Install Growth")


# ============================================================================
# PAGES
# ============================================================================

if page == "📤 Upload Data":
    st.title("📤 Upload New Data")
    st.markdown("### Update dashboard with new monthly data")

    st.info("Upload CSV files exported from Shopify App Store Ads to update the dashboard data.")

    # Data period
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Period Start Date")
    with col2:
        end_date = st.date_input("Period End Date")

    if st.button("Update Period"):
        st.session_state.data_period = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
        st.success(f"Period updated to: {st.session_state.data_period}")

    st.markdown("---")

    # Campaign Metrics Upload
    st.subheader("1. Campaign Metrics (Daily)")
    st.markdown("Upload: `shopify-app-store-ads-campaign-metrics-by-day.csv`")

    campaign_file = st.file_uploader("Campaign Metrics CSV", type=['csv'], key='campaign_upload')

    if campaign_file:
        df, error = process_campaign_metrics_upload(campaign_file)
        if error:
            st.error(f"Error: {error}")
        else:
            st.success(f"Loaded {len(df)} campaigns")
            st.dataframe(df)
            if st.button("Apply Campaign Data"):
                st.session_state.df_campaigns = df
                st.success("Campaign data updated!")

    st.markdown("---")

    # Keywords Upload
    st.subheader("2. Keywords Data")
    st.markdown("Upload: `shopify-app-store-ads-keywords.csv`")

    campaign_select = st.selectbox(
        "Select Campaign for Keywords:",
        ["ProductReview", "Competitors", "Review-variations", "Features"]
    )

    keywords_file = st.file_uploader("Keywords CSV", type=['csv'], key='keywords_upload')

    if keywords_file:
        df, error = process_keywords_upload(keywords_file, campaign_select)
        if error:
            st.error(f"Error: {error}")
        else:
            st.success(f"Loaded {len(df)} keywords")
            st.dataframe(df)
            if st.button("Apply Keywords Data"):
                if campaign_select == "ProductReview":
                    st.session_state.df_kw_product_review = df
                elif campaign_select == "Competitors":
                    st.session_state.df_kw_competitors = df
                elif campaign_select == "Review-variations":
                    st.session_state.df_kw_review_variations = df
                else:
                    st.session_state.df_kw_features = df
                st.success(f"{campaign_select} keywords updated!")

    st.markdown("---")

    # Search Terms Upload
    st.subheader("3. Search Terms Data")
    st.markdown("Upload: `shopify-app-store-ads-search-terms.csv`")

    search_file = st.file_uploader("Search Terms CSV", type=['csv'], key='search_upload')

    if search_file:
        try:
            df = pd.read_csv(search_file)
            st.success(f"Loaded {len(df)} search terms")
            st.dataframe(df.head(20))
            st.info("Search terms analysis will be added in future updates")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")

    # Reset to defaults
    st.subheader("Reset Data")
    if st.button("Reset to Default Data", type="secondary"):
        st.session_state.data_loaded = False
        load_data()
        st.success("Data reset to defaults!")
        st.rerun()

elif page == "Executive Summary":
    st.title("Judge.me Shopify Ads Analysis")
    st.markdown("### Executive Summary - Keyword Discovery for Install Growth")

    df_campaigns = st.session_state.df_campaigns

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend", f"${df_campaigns['Total Spend'].sum():,.0f}")
    with col2:
        st.metric("Total Installs", f"{df_campaigns['Total Installs'].sum():,}")
    with col3:
        avg_cpi = df_campaigns['Total Spend'].sum() / df_campaigns['Total Installs'].sum()
        st.metric("Average CPI", f"${avg_cpi:.2f}")
    with col4:
        overall_roas = df_campaigns['Total Revenue'].sum() / df_campaigns['Total Spend'].sum() * 100
        st.metric("Overall ROAS", f"{overall_roas:.1f}%")

    st.markdown("---")

    # Key Findings
    st.subheader("Key Findings for Install Growth")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Top Performing Keywords (by Install Volume):**
        1. `reviews` (exact) - 4,594 installs, $3.01 CPI
        2. `review` (exact) - 3,201 installs, $1.92 CPI
        3. `product review` (broad) - 2,033 installs
        4. `amazon reviews importer` - 1,356 installs
        5. `product reviews` (exact) - 1,244 installs

        **Highest ROAS Keywords:**
        1. `yotpo reviews` - 341% ROAS
        2. `loox - photo reviews` - 190% ROAS
        3. `okendo` - 151.5% ROAS
        4. `loox review` - 76.1% ROAS
        5. `customer reviews` - 60.6% ROAS
        """)

    with col2:
        st.markdown(f"""
        **Immediate Keyword Opportunities:**
        - **{len(st.session_state.df_new_keywords)} new keywords** identified for testing
        - **{len(st.session_state.df_new_keywords[st.session_state.df_new_keywords['Priority'] == 'HIGH'])} HIGH priority** keywords ready to launch
        - Est. **1,000+ additional installs/month** potential

        **Keywords to Action:**
        - **{len(st.session_state.df_keywords_to_pause)} keywords** to pause/reduce bid
        - **{len(st.session_state.df_bid_increases)} keywords** to increase bid
        - Estimated savings: **$300-500/month** reallocation

        **Competitor Gaps:**
        - `stamped.io` - Not targeted (major competitor)
        - `fera reviews` - Untapped opportunity
        - `vitals reviews` - Growing segment
        """)

    st.markdown("---")

    # Campaign Overview Chart
    st.subheader("Campaign Performance Overview")

    fig = px.bar(
        df_campaigns,
        x='Campaign',
        y=['Total Installs', 'Total Customers'],
        barmode='group',
        title='Installs vs Customers by Campaign',
        color_discrete_sequence=['#4CAF50', '#2196F3']
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Campaign Performance":
    st.title("Campaign Performance Analysis")

    df_campaigns = st.session_state.df_campaigns

    st.subheader("All Campaigns Summary")

    df_display = df_campaigns.copy()
    df_display['Total Spend'] = df_display['Total Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['Avg CPI'] = df_display['Avg CPI'].apply(lambda x: f"${x:.2f}")
    df_display['Avg Install Rate'] = df_display['Avg Install Rate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['Total Revenue'] = df_display['Total Revenue'].apply(lambda x: f"${x:,.2f}")
    df_display['ROAS'] = df_display['ROAS'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(df_display, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            df_campaigns,
            values='Total Installs',
            names='Campaign',
            title='Install Distribution by Campaign',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_campaigns,
            x='Campaign',
            y='ROAS',
            title='ROAS by Campaign (%)',
            color='ROAS',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Keyword Analysis":
    st.title("Keyword Performance Analysis")

    campaign_select = st.selectbox(
        "Select Campaign:",
        ["ProductReview", "Competitors", "Review-variations", "Features"]
    )

    if campaign_select == "ProductReview":
        df_selected = st.session_state.df_kw_product_review
    elif campaign_select == "Competitors":
        df_selected = st.session_state.df_kw_competitors
    elif campaign_select == "Review-variations":
        df_selected = st.session_state.df_kw_review_variations
    else:
        df_selected = st.session_state.df_kw_features

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Keywords", len(df_selected))
    with col2:
        st.metric("Total Installs", f"{df_selected['Installs'].sum():,}")
    with col3:
        st.metric("Total Spend", f"${df_selected['Spend'].sum():,.2f}")
    with col4:
        avg_cpi = df_selected['Spend'].sum() / df_selected['Installs'].sum() if df_selected['Installs'].sum() > 0 else 0
        st.metric("Avg CPI", f"${avg_cpi:.2f}")

    st.subheader(f"All Keywords - {campaign_select} Campaign")

    df_display = df_selected.copy()
    df_display['Spend'] = df_display['Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['CPI'] = df_display['CPI'].apply(lambda x: f"${x:.2f}")
    df_display['InstallRate'] = df_display['InstallRate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['ROAS'] = df_display['ROAS'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(df_display, use_container_width=True)

    st.subheader("Keyword Performance Scatter")
    fig = px.scatter(
        df_selected,
        x='CPI',
        y='Installs',
        size='Spend',
        color='InstallRate',
        hover_name='Keyword',
        title='CPI vs Installs (bubble size = spend)',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "New Keywords":
    st.title("New Keyword Recommendations")
    st.markdown("### Focus: Keyword Discovery for Install Growth")

    df_new_keywords = st.session_state.df_new_keywords
    high_priority = df_new_keywords[df_new_keywords['Priority'] == 'HIGH']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total New Keywords", len(df_new_keywords))
    with col2:
        st.metric("HIGH Priority", len(high_priority), delta="Launch First")
    with col3:
        st.metric("Est. Monthly Installs", f"{df_new_keywords['Est. Installs'].sum():,}")
    with col4:
        avg_bid = df_new_keywords['Suggested Bid'].mean()
        st.metric("Avg Suggested Bid", f"${avg_bid:.2f}")

    st.markdown("---")

    priority_filter = st.multiselect(
        "Filter by Priority:",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )

    df_filtered = df_new_keywords[df_new_keywords['Priority'].isin(priority_filter)]

    if "HIGH" in priority_filter:
        st.subheader("HIGH Priority Keywords (Launch Immediately)")
        high_df = df_filtered[df_filtered['Priority'] == 'HIGH']

        for _, row in high_df.iterrows():
            with st.expander(f"**{row['Keyword']}** ({row['Match Type']}) - Bid: ${row['Suggested Bid']:.2f}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Campaign:** {row['Campaign']}")
                with col2:
                    st.markdown(f"**Est. Impressions:** {row['Est. Impressions']:,}")
                with col3:
                    st.markdown(f"**Est. Installs:** {row['Est. Installs']}")
                st.markdown(f"**Rationale:** {row['Rationale']}")

    st.subheader("All Keyword Recommendations")

    df_display = df_filtered.copy()
    df_display['Suggested Bid'] = df_display['Suggested Bid'].apply(lambda x: f"${x:.2f}")

    st.dataframe(df_display, use_container_width=True)

    csv = df_new_keywords.to_csv(index=False)
    st.download_button(
        label="Download All Recommendations as CSV",
        data=csv,
        file_name="judge_me_new_keywords.csv",
        mime="text/csv"
    )

elif page == "Keywords to Pause":
    st.title("Keywords to Pause or Reduce")

    df_keywords_to_pause = st.session_state.df_keywords_to_pause
    pause_count = len(df_keywords_to_pause[df_keywords_to_pause['Action'] == 'PAUSE'])
    reduce_count = len(df_keywords_to_pause[df_keywords_to_pause['Action'] == 'REDUCE BID'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Keywords to Action", len(df_keywords_to_pause))
    with col2:
        st.metric("To Pause", pause_count)
    with col3:
        st.metric("To Reduce Bid", reduce_count)

    st.markdown("---")

    st.subheader("PAUSE These Keywords")
    pause_df = df_keywords_to_pause[df_keywords_to_pause['Action'] == 'PAUSE']

    for _, row in pause_df.iterrows():
        st.error(f"**{row['Keyword']}** ({row['Match']}) - {row['Campaign']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"Spend: ${row['Spend']:,.2f}")
            st.markdown(f"Installs: {row['Installs']}")
        with col2:
            st.markdown(f"**Reason:** {row['Reason']}")
        st.markdown("---")

    st.subheader("REDUCE Bids on These Keywords")
    reduce_df = df_keywords_to_pause[df_keywords_to_pause['Action'] == 'REDUCE BID']

    for _, row in reduce_df.iterrows():
        st.warning(f"**{row['Keyword']}** ({row['Match']}) - {row['Campaign']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"Spend: ${row['Spend']:,.2f}")
        with col2:
            st.markdown(f"**Action:** {row['Reason']}")
        st.markdown("---")

elif page == "Bid Recommendations":
    st.title("Bid Increase Recommendations")

    df_bid_increases = st.session_state.df_bid_increases

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Keywords to Increase", len(df_bid_increases))
    with col2:
        avg_increase = (df_bid_increases['Recommended Bid'] - df_bid_increases['Current Bid']).mean()
        st.metric("Avg Bid Increase", f"+${avg_increase:.2f}")

    st.markdown("---")

    for _, row in df_bid_increases.iterrows():
        increase = row['Recommended Bid'] - row['Current Bid']

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            st.markdown(f"**{row['Keyword']}** ({row['Match']})")
            st.caption(row['Campaign'])
        with col2:
            st.markdown(f"Current: **${row['Current Bid']:.2f}**")
        with col3:
            st.markdown(f"New: **${row['Recommended Bid']:.2f}**")
        with col4:
            st.markdown(f"<span style='color: green;'>+${increase:.2f}</span>", unsafe_allow_html=True)

        st.caption(row['Reason'])
        st.markdown("---")

elif page == "Search Term Opportunities":
    st.title("Search Term Opportunities")

    df_search_opportunities = st.session_state.df_search_opportunities
    total_installs = df_search_opportunities['Installs'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Search Terms Identified", len(df_search_opportunities))
    with col2:
        st.metric("Total Installs", f"{total_installs:,}")
    with col3:
        avg_cpi = df_search_opportunities['Spend'].sum() / total_installs if total_installs > 0 else 0
        st.metric("Avg CPI", f"${avg_cpi:.2f}")

    st.markdown("---")

    df_display = df_search_opportunities.copy()
    df_display['Spend'] = df_display['Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['CPI'] = df_display['CPI'].apply(lambda x: f"${x:.2f}")
    df_display['InstallRate'] = df_display['InstallRate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['Suggested Bid'] = df_display['Suggested Bid'].apply(lambda x: f"${x:.2f}")

    st.dataframe(df_display, use_container_width=True)

elif page == "Negative Keywords":
    st.title("Existing Negative Keywords")

    negative_keywords_summary = {
        'ProductReview Campaign': [
            'judge.me (broad)', 'judge me (broad)', 'loox (various)', 'trustoo (various)',
            'yotpo (various)', 'okendo (various)', 'rivo (various)', 'trustpilot (various)'
        ],
        'Review-variations Campaign': [
            'judge (broad)', 'Google Reviews (broad + exact)', 'ali review (broad)',
            'amazon review (broad)', 'etsy reviews (broad)', 'testimonials slider (exact)'
        ],
        'Features Campaign': [
            'judge.me branded terms', 'competitor names', 'reviews (exact)'
        ],
        'Trust Campaign': [
            'trustpilot (exact)', 'trust pilot (exact)', 'social media icons'
        ]
    }

    for campaign, keywords in negative_keywords_summary.items():
        with st.expander(f"**{campaign}** ({len(keywords)} categories)"):
            for kw in keywords:
                st.markdown(f"- {kw}")

elif page == "Action Checklist":
    st.title("Action Checklist")

    st.subheader("IMMEDIATE ACTIONS (This Week)")

    actions_immediate = [
        ("PAUSE", "customer feedback (broad)", "Review-variations"),
        ("PAUSE", "feedback app (broad)", "Review-variations"),
        ("INCREASE BID", "okendo to $5.00", "Competitors"),
        ("INCREASE BID", "yotpo reviews to $3.50", "Competitors"),
        ("ADD KEYWORD", "testimonials (exact)", "Review-variations"),
        ("ADD KEYWORD", "loox reviews (exact)", "Competitors"),
    ]

    for action, keyword, campaign in actions_immediate:
        st.checkbox(f"**{action}:** `{keyword}` in {campaign}", key=f"imm_{keyword}")

    st.markdown("---")

    st.subheader("SHORT-TERM ACTIONS (Next 2 Weeks)")

    actions_short = [
        "Add all HIGH priority new keywords (10 keywords)",
        "Reduce bid on google reviews/review to $3.50",
        "Add competitor keywords: stamped.io, fera reviews",
    ]

    for action in actions_short:
        st.checkbox(action, key=f"short_{action[:20]}")


# Footer
st.markdown("---")
st.caption("Judge.me Shopify Ads Analysis Dashboard | Focus: Keyword Discovery for Install Growth")
