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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA - All campaign data embedded for standalone dashboard
# ============================================================================

# Campaign Summary Data
campaign_data = {
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
}
df_campaigns = pd.DataFrame(campaign_data)

# Keywords Performance Data - ProductReview Campaign
keywords_product_review = [
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
]
df_kw_product_review = pd.DataFrame(keywords_product_review)

# Keywords Performance Data - Competitors Campaign
keywords_competitors = [
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
]
df_kw_competitors = pd.DataFrame(keywords_competitors)

# Keywords Performance Data - Review Variations Campaign
keywords_review_variations = [
    {'Keyword': 'testimonial', 'Match': 'broad', 'Bid': 2.5, 'Impressions': 6402, 'Clicks': 784, 'Installs': 474, 'Spend': 1960.0, 'CPI': 4.14, 'InstallRate': 0.60, 'ROAS': 13.8},
    {'Keyword': 'product rating', 'Match': 'broad', 'Bid': 4.5, 'Impressions': 5924, 'Clicks': 270, 'Installs': 185, 'Spend': 1215.0, 'CPI': 6.57, 'InstallRate': 0.69, 'ROAS': 24.9},
    {'Keyword': 'customer feedback', 'Match': 'broad', 'Bid': 5.0, 'Impressions': 5425, 'Clicks': 320, 'Installs': 185, 'Spend': 1600.0, 'CPI': 8.65, 'InstallRate': 0.58, 'ROAS': 9.5},
    {'Keyword': 'testimonial', 'Match': 'exact', 'Bid': 2.82, 'Impressions': 2714, 'Clicks': 337, 'Installs': 202, 'Spend': 950.34, 'CPI': 4.70, 'InstallRate': 0.60, 'ROAS': 23.9},
    {'Keyword': 'product rating', 'Match': 'exact', 'Bid': 3.0, 'Impressions': 490, 'Clicks': 42, 'Installs': 28, 'Spend': 126.0, 'CPI': 4.50, 'InstallRate': 0.67, 'ROAS': 0},
    {'Keyword': 'feedback app', 'Match': 'broad', 'Bid': 3.0, 'Impressions': 415, 'Clicks': 10, 'Installs': 4, 'Spend': 30.0, 'CPI': 7.50, 'InstallRate': 0.40, 'ROAS': 0},
    {'Keyword': 'ratings', 'Match': 'exact', 'Bid': 5.0, 'Impressions': 342, 'Clicks': 124, 'Installs': 102, 'Spend': 620.0, 'CPI': 6.08, 'InstallRate': 0.82, 'ROAS': 26.6},
]
df_kw_review_variations = pd.DataFrame(keywords_review_variations)

# Keywords Performance Data - Features Campaign
keywords_features = [
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
]
df_kw_features = pd.DataFrame(keywords_features)

# Search Terms with High Potential (not yet added as keywords)
search_term_opportunities = [
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
]
df_search_opportunities = pd.DataFrame(search_term_opportunities)

# NEW KEYWORD RECOMMENDATIONS - Primary Focus
new_keyword_recommendations = [
    # High Priority - High Volume + Good Intent
    {'Keyword': 'testimonials', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 3500, 'Est. Installs': 280, 'Rationale': 'High volume search term with 321 installs via broad match'},
    {'Keyword': 'testimonial slider', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 1500, 'Est. Installs': 100, 'Rationale': '127 installs from broad match, specific feature intent'},
    {'Keyword': 'rating', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 4.00, 'Est. Impressions': 1500, 'Est. Installs': 120, 'Rationale': '146 installs, 77% install rate - strong performer'},
    {'Keyword': 'loox reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.50, 'Est. Impressions': 3000, 'Est. Installs': 95, 'Rationale': 'Competitor comparison intent, 100 installs via broad'},
    {'Keyword': 'star rating', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'HIGH', 'Suggested Bid': 3.50, 'Est. Impressions': 800, 'Est. Installs': 60, 'Rationale': 'Core feature term, high relevance'},

    # High Priority - Competitor Terms to Expand
    {'Keyword': 'stamped.io', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 2000, 'Est. Installs': 80, 'Rationale': 'Major competitor not yet targeted'},
    {'Keyword': 'stamped reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 3.00, 'Est. Impressions': 1200, 'Est. Installs': 50, 'Rationale': 'Competitor + reviews intent'},
    {'Keyword': 'fera reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 800, 'Est. Installs': 35, 'Rationale': 'Growing competitor, untapped'},
    {'Keyword': 'vitals reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 500, 'Est. Installs': 25, 'Rationale': 'Vitals app users seeking reviews'},
    {'Keyword': 'growave reviews', 'Match Type': 'exact', 'Campaign': 'Competitors', 'Priority': 'HIGH', 'Suggested Bid': 2.50, 'Est. Impressions': 400, 'Est. Installs': 20, 'Rationale': 'Multi-feature competitor'},

    # Medium Priority - Feature Terms
    {'Keyword': 'photo review app', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 500, 'Est. Installs': 40, 'Rationale': 'Feature-specific, high intent'},
    {'Keyword': 'video review app', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 400, 'Est. Installs': 30, 'Rationale': 'Video reviews feature intent'},
    {'Keyword': 'review request email', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 600, 'Est. Installs': 45, 'Rationale': 'Core feature, automation intent'},
    {'Keyword': 'google shopping reviews', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 800, 'Est. Installs': 50, 'Rationale': 'SEO/Rich snippet intent'},
    {'Keyword': 'aliexpress reviews', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 1200, 'Est. Installs': 80, 'Rationale': 'Import feature, dropship audience'},
    {'Keyword': 'ebay reviews importer', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 400, 'Est. Installs': 25, 'Rationale': 'Import feature expansion'},
    {'Keyword': 'review carousel', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 500, 'Est. Installs': 35, 'Rationale': 'Display feature intent'},
    {'Keyword': 'review widget', 'Match Type': 'broad', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 4.00, 'Est. Impressions': 800, 'Est. Installs': 50, 'Rationale': 'Expand widget coverage'},

    # Medium Priority - Use Case Terms
    {'Keyword': 'dropshipping reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 3.50, 'Est. Impressions': 600, 'Est. Installs': 40, 'Rationale': 'Target dropship segment'},
    {'Keyword': 'shopify store reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 2.50, 'Est. Impressions': 1000, 'Est. Installs': 70, 'Rationale': 'Platform-specific intent'},
    {'Keyword': 'ecommerce reviews', 'Match Type': 'exact', 'Campaign': 'ProductReview', 'Priority': 'MEDIUM', 'Suggested Bid': 3.00, 'Est. Impressions': 500, 'Est. Installs': 35, 'Rationale': 'Broad ecommerce audience'},

    # Lower Priority - Test Keywords
    {'Keyword': 'social proof', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'LOW', 'Suggested Bid': 3.00, 'Est. Impressions': 400, 'Est. Installs': 20, 'Rationale': 'Conceptual term, test performance'},
    {'Keyword': 'trust badges', 'Match Type': 'exact', 'Campaign': 'Review-variations', 'Priority': 'LOW', 'Suggested Bid': 2.50, 'Est. Impressions': 500, 'Est. Installs': 25, 'Rationale': 'Related concept, may convert'},
    {'Keyword': 'nps survey', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'LOW', 'Suggested Bid': 3.00, 'Est. Impressions': 300, 'Est. Installs': 15, 'Rationale': 'NPS feature awareness'},
    {'Keyword': 'review syndication', 'Match Type': 'exact', 'Campaign': 'Features', 'Priority': 'LOW', 'Suggested Bid': 4.00, 'Est. Impressions': 200, 'Est. Installs': 15, 'Rationale': 'Enterprise feature'},
]
df_new_keywords = pd.DataFrame(new_keyword_recommendations)

# Keywords to Pause/Reduce
keywords_to_pause = [
    {'Keyword': 'customer feedback', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'PAUSE', 'Reason': 'High CPI ($8.65), low ROAS (9.5%), catching irrelevant searches like "checkout customizer", "customer accounts"', 'Spend': 1600.0, 'Installs': 185},
    {'Keyword': 'feedback app', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'PAUSE', 'Reason': 'Very low relevance - catching "free apps", "mobile app builder", "bundle apps"', 'Spend': 30.0, 'Installs': 4},
    {'Keyword': 'product rating', 'Match': 'broad', 'Campaign': 'Review-variations', 'Action': 'REDUCE BID', 'Reason': 'Catching shipping rate, product label searches. High CPI ($6.57). Reduce bid to $3.00', 'Spend': 1215.0, 'Installs': 185},
    {'Keyword': 'carousel', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'REDUCE BID', 'Reason': 'Very high CPI ($16.98), low install rate (35%). Reduce bid to $3.00', 'Spend': 696.0, 'Installs': 41},
    {'Keyword': 'ugc', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'REDUCE BID', 'Reason': 'Highest CPI ($18.29), low relevance. Reduce bid to $4.00 or pause', 'Spend': 567.0, 'Installs': 31},
    {'Keyword': 'google reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Action': 'REDUCE BID', 'Reason': 'High CPI ($10.62), users may expect Google My Business. Reduce to $3.50', 'Spend': 3260.0, 'Installs': 307},
    {'Keyword': 'google review', 'Match': 'exact', 'Campaign': 'ProductReview', 'Action': 'REDUCE BID', 'Reason': 'High CPI ($10.33), same issue as google reviews. Reduce to $3.50', 'Spend': 1860.0, 'Installs': 180},
    {'Keyword': 'q&a', 'Match': 'broad', 'Campaign': 'Features', 'Action': 'PAUSE', 'Reason': 'Very high CPI ($18.00), low install rate (33%), low relevance', 'Spend': 72.0, 'Installs': 4},
]
df_keywords_to_pause = pd.DataFrame(keywords_to_pause)

# BID INCREASE RECOMMENDATIONS
bid_increase_recommendations = [
    {'Keyword': 'okendo', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 3.50, 'Recommended Bid': 5.00, 'Reason': 'Highest ROAS (151.5%), highest customer conversion (25.7%). Increase visibility.'},
    {'Keyword': 'yotpo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.50, 'Reason': 'Exceptional ROAS (341%), needs more volume. High intent competitor search.'},
    {'Keyword': 'loox - photo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 190.4%, install rate 85%. Underpriced.'},
    {'Keyword': 'loox review', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 76.1%, good volume. Capture more competitor traffic.'},
    {'Keyword': 'shopify product reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 1.00, 'Recommended Bid': 2.00, 'Reason': 'Best CPI ($1.16), 86% install rate, 50.3% ROAS. Severely underpriced.'},
    {'Keyword': 'customer reviews', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 60.6%, install rate 83%, low CPI. Great performer.'},
    {'Keyword': 'reviews app', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'ROAS 41%, install rate 76%. Strong intent keyword.'},
    {'Keyword': 'review', 'Match': 'exact', 'Campaign': 'ProductReview', 'Current Bid': 1.50, 'Recommended Bid': 2.00, 'Reason': 'Second best CPI ($1.92), 78% install rate, 37.7% ROAS. Volume driver.'},
    {'Keyword': 'trustoo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'Excellent CPI ($2.47), 81% install rate. Needs more visibility.'},
    {'Keyword': 'rivo reviews', 'Match': 'exact', 'Campaign': 'Competitors', 'Current Bid': 2.00, 'Recommended Bid': 3.00, 'Reason': 'Good CPI ($2.69), 74% install rate. Emerging competitor.'},
    {'Keyword': 'reviews importer', 'Match': 'exact', 'Campaign': 'Features', 'Current Bid': 3.20, 'Recommended Bid': 4.00, 'Reason': 'Good CPI ($4.35), 74% install rate. Feature-specific intent.'},
    {'Keyword': 'review importer', 'Match': 'exact', 'Campaign': 'Features', 'Current Bid': 3.60, 'Recommended Bid': 4.50, 'Reason': 'Good volume, 77% install rate. Import is key feature.'},
]
df_bid_increases = pd.DataFrame(bid_increase_recommendations)

# Existing Negative Keywords Summary
negative_keywords_summary = {
    'ProductReview Campaign': [
        'judge.me (broad)', 'judge me (broad)', 'loox (various)', 'trustoo (various)',
        'yotpo (various)', 'okendo (various)', 'rivo (various)', 'trustpilot (various)',
        'lai reviews', 'klaviyo reviews', 'tydal reviews', 'vitals reviews'
    ],
    'Review-variations Campaign': [
        'judge (broad)', 'Google Reviews (broad + exact)', 'ali review (broad)',
        'amazon review (broad)', 'etsy reviews (broad)', 'testimonials slider (exact)',
        'import reviews (exact)', 'fake reviews (exact)', 'free (exact)', 'apps (exact)',
        'shopify (exact)', 'product (exact)', 'video (exact)', 'many product-related terms'
    ],
    'Features Campaign': [
        'judge.me branded terms', 'competitor names', 'reviews (exact)',
        'product reviews (exact)', 'generic terms'
    ],
    'Trust Campaign': [
        'trustpilot (exact)', 'trust pilot (exact)', 'social media icons',
        'social login', 'social media (various)'
    ]
}

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.image("https://judge.me/assets/logo-cd7d77c3a9842ec7f0dcd21298bc0c5e23c16c9bea09b28f8d3f0d1e5b0f1b8a.svg", width=150)
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Section:",
    ["Executive Summary", "Campaign Performance", "Keyword Analysis",
     "New Keywords", "Keywords to Pause", "Bid Recommendations",
     "Search Term Opportunities", "Negative Keywords", "Action Checklist"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Analysis Period:**")
st.sidebar.markdown("Aug 21, 2025 - Feb 18, 2026")
st.sidebar.markdown("**Focus:**")
st.sidebar.markdown("Keyword Discovery for Install Growth")

# ============================================================================
# PAGES
# ============================================================================

if page == "Executive Summary":
    st.title("Judge.me Shopify Ads Analysis")
    st.markdown("### Executive Summary - Keyword Discovery for Install Growth")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend", "$70,682", delta=None)
    with col2:
        st.metric("Total Installs", "18,176", delta="+2,127 from Features")
    with col3:
        st.metric("Average CPI", "$3.89", delta="-$0.45 vs prev period")
    with col4:
        st.metric("Overall ROAS", "26.0%", delta=None)

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
        st.markdown("""
        **Immediate Keyword Opportunities:**
        - **25 new keywords** identified for testing
        - **10 HIGH priority** keywords ready to launch
        - Est. **1,000+ additional installs/month** potential

        **Keywords to Action:**
        - **8 keywords** to pause/reduce bid
        - **12 keywords** to increase bid
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

    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Best CPI Campaign:**")
        st.markdown("ProductReview - $3.23")
    with col2:
        st.markdown("**Best ROAS Campaign:**")
        st.markdown("Competitors - 61.2%")
    with col3:
        st.markdown("**Highest Volume:**")
        st.markdown("ProductReview - 13,539 installs")

elif page == "Campaign Performance":
    st.title("Campaign Performance Analysis")

    # Campaign metrics table
    st.subheader("All Campaigns Summary")

    # Format the dataframe for display
    df_display = df_campaigns.copy()
    df_display['Total Spend'] = df_display['Total Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['Avg CPI'] = df_display['Avg CPI'].apply(lambda x: f"${x:.2f}")
    df_display['Avg Install Rate'] = df_display['Avg Install Rate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['Total Revenue'] = df_display['Total Revenue'].apply(lambda x: f"${x:,.2f}")
    df_display['ROAS'] = df_display['ROAS'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(df_display, use_container_width=True)

    # Charts
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

    # CPI Comparison
    st.subheader("Cost Per Install Comparison")
    fig = px.bar(
        df_campaigns,
        x='Campaign',
        y='Avg CPI',
        title='Average CPI by Campaign',
        color='Avg CPI',
        color_continuous_scale='RdYlGn_r'
    )
    fig.add_hline(y=df_campaigns['Avg CPI'].mean(), line_dash="dash",
                  annotation_text=f"Avg: ${df_campaigns['Avg CPI'].mean():.2f}")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Keyword Analysis":
    st.title("Keyword Performance Analysis")

    campaign_select = st.selectbox(
        "Select Campaign:",
        ["ProductReview", "Competitors", "Review-variations", "Features"]
    )

    if campaign_select == "ProductReview":
        df_selected = df_kw_product_review
    elif campaign_select == "Competitors":
        df_selected = df_kw_competitors
    elif campaign_select == "Review-variations":
        df_selected = df_kw_review_variations
    else:
        df_selected = df_kw_features

    # Metrics
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

    # Full keyword table
    st.subheader(f"All Keywords - {campaign_select} Campaign")

    df_display = df_selected.copy()
    df_display['Spend'] = df_display['Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['CPI'] = df_display['CPI'].apply(lambda x: f"${x:.2f}")
    df_display['InstallRate'] = df_display['InstallRate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['ROAS'] = df_display['ROAS'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(df_display, use_container_width=True)

    # Scatter plot
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
    fig.add_vline(x=df_selected['CPI'].mean(), line_dash="dash", line_color="gray")
    fig.add_hline(y=df_selected['Installs'].mean(), line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

elif page == "New Keywords":
    st.title("New Keyword Recommendations")
    st.markdown("### Focus: Keyword Discovery for Install Growth")

    # Summary metrics
    high_priority = df_new_keywords[df_new_keywords['Priority'] == 'HIGH']
    med_priority = df_new_keywords[df_new_keywords['Priority'] == 'MEDIUM']
    low_priority = df_new_keywords[df_new_keywords['Priority'] == 'LOW']

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

    # Priority filter
    priority_filter = st.multiselect(
        "Filter by Priority:",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )

    df_filtered = df_new_keywords[df_new_keywords['Priority'].isin(priority_filter)]

    # HIGH Priority Section
    if "HIGH" in priority_filter:
        st.subheader("HIGH Priority Keywords (Launch Immediately)")
        high_df = df_filtered[df_filtered['Priority'] == 'HIGH']

        for _, row in high_df.iterrows():
            with st.expander(f"**{row['Keyword']}** ({row['Match Type']}) - Bid: ${row['Suggested Bid']:.2f}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Campaign:** {row['Campaign']}")
                    st.markdown(f"**Match Type:** {row['Match Type']}")
                with col2:
                    st.markdown(f"**Est. Impressions:** {row['Est. Impressions']:,}")
                    st.markdown(f"**Est. Installs:** {row['Est. Installs']}")
                with col3:
                    st.markdown(f"**Suggested Bid:** ${row['Suggested Bid']:.2f}")
                st.markdown(f"**Rationale:** {row['Rationale']}")

    # Full table
    st.subheader("All Keyword Recommendations")

    df_display = df_filtered.copy()
    df_display['Suggested Bid'] = df_display['Suggested Bid'].apply(lambda x: f"${x:.2f}")
    df_display['Est. Impressions'] = df_display['Est. Impressions'].apply(lambda x: f"{x:,}")

    st.dataframe(df_display, use_container_width=True)

    # Download button
    csv = df_new_keywords.to_csv(index=False)
    st.download_button(
        label="Download All Recommendations as CSV",
        data=csv,
        file_name="judge_me_new_keywords.csv",
        mime="text/csv"
    )

elif page == "Keywords to Pause":
    st.title("Keywords to Pause or Reduce")
    st.markdown("### Underperforming Keywords Draining Budget")

    # Summary
    total_wasted = df_keywords_to_pause['Spend'].sum()
    pause_count = len(df_keywords_to_pause[df_keywords_to_pause['Action'] == 'PAUSE'])
    reduce_count = len(df_keywords_to_pause[df_keywords_to_pause['Action'] == 'REDUCE BID'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Keywords to Action", len(df_keywords_to_pause))
    with col2:
        st.metric("To Pause", pause_count, delta="Immediate")
    with col3:
        st.metric("To Reduce Bid", reduce_count)

    st.markdown("---")

    # PAUSE section
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

    # REDUCE BID section
    st.subheader("REDUCE Bids on These Keywords")
    reduce_df = df_keywords_to_pause[df_keywords_to_pause['Action'] == 'REDUCE BID']

    for _, row in reduce_df.iterrows():
        st.warning(f"**{row['Keyword']}** ({row['Match']}) - {row['Campaign']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"Spend: ${row['Spend']:,.2f}")
            st.markdown(f"Installs: {row['Installs']}")
        with col2:
            st.markdown(f"**Action:** {row['Reason']}")
        st.markdown("---")

    # Full table
    st.subheader("Complete List")
    st.dataframe(df_keywords_to_pause, use_container_width=True)

elif page == "Bid Recommendations":
    st.title("Bid Increase Recommendations")
    st.markdown("### Maximize Install Volume from Top Performers")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Keywords to Increase", len(df_bid_increases))
    with col2:
        avg_increase = (df_bid_increases['Recommended Bid'] - df_bid_increases['Current Bid']).mean()
        st.metric("Avg Bid Increase", f"+${avg_increase:.2f}")

    st.markdown("---")

    # Detailed recommendations
    for _, row in df_bid_increases.iterrows():
        increase = row['Recommended Bid'] - row['Current Bid']
        increase_pct = (increase / row['Current Bid']) * 100

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            st.markdown(f"**{row['Keyword']}** ({row['Match']})")
            st.caption(row['Campaign'])
        with col2:
            st.markdown(f"Current: **${row['Current Bid']:.2f}**")
        with col3:
            st.markdown(f"Recommended: **${row['Recommended Bid']:.2f}**")
        with col4:
            st.markdown(f"<span style='color: green;'>+${increase:.2f} ({increase_pct:.0f}%)</span>",
                       unsafe_allow_html=True)

        st.caption(row['Reason'])
        st.markdown("---")

    # Chart
    st.subheader("Bid Comparison")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current Bid',
        x=df_bid_increases['Keyword'],
        y=df_bid_increases['Current Bid'],
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        name='Recommended Bid',
        x=df_bid_increases['Keyword'],
        y=df_bid_increases['Recommended Bid'],
        marker_color='green'
    ))
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        title='Current vs Recommended Bids'
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Search Term Opportunities":
    st.title("Search Term Opportunities")
    st.markdown("### High-Performing Search Terms to Add as Keywords")

    st.info("These search terms are currently triggered by broad match keywords but should be added as exact match for better control and potential bid optimization.")

    # Metrics
    total_installs = df_search_opportunities['Installs'].sum()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Search Terms Identified", len(df_search_opportunities))
    with col2:
        st.metric("Total Installs", f"{total_installs:,}")
    with col3:
        avg_cpi = df_search_opportunities['Spend'].sum() / total_installs
        st.metric("Avg CPI", f"${avg_cpi:.2f}")

    st.markdown("---")

    # Full table
    df_display = df_search_opportunities.copy()
    df_display['Spend'] = df_display['Spend'].apply(lambda x: f"${x:,.2f}")
    df_display['CPI'] = df_display['CPI'].apply(lambda x: f"${x:.2f}")
    df_display['InstallRate'] = df_display['InstallRate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['Suggested Bid'] = df_display['Suggested Bid'].apply(lambda x: f"${x:.2f}")

    st.dataframe(df_display, use_container_width=True)

    # Detailed cards
    st.subheader("Top Opportunities")

    top_opportunities = df_search_opportunities.nlargest(5, 'Installs')

    for _, row in top_opportunities.iterrows():
        with st.expander(f"**{row['Search Term']}** - {row['Installs']} installs"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Impressions:** {row['Impressions']:,}")
                st.markdown(f"**Clicks:** {row['Clicks']:,}")
            with col2:
                st.markdown(f"**Installs:** {row['Installs']}")
                st.markdown(f"**CPI:** ${row['CPI']:.2f}")
            with col3:
                st.markdown(f"**Install Rate:** {row['InstallRate']*100:.1f}%")
                st.markdown(f"**Suggested Bid:** ${row['Suggested Bid']:.2f}")
            st.markdown(f"**Triggered By:** {row['Triggered By']}")
            st.markdown(f"**Recommendation:** {row['Recommendation']}")

elif page == "Negative Keywords":
    st.title("Existing Negative Keywords")
    st.markdown("### Current Negative Keyword Strategy by Campaign")

    for campaign, keywords in negative_keywords_summary.items():
        with st.expander(f"**{campaign}** ({len(keywords)} categories)"):
            for kw in keywords:
                st.markdown(f"- {kw}")

    st.markdown("---")

    st.subheader("Recommended Additional Negative Keywords")

    additional_negatives = [
        {'Keyword': 'checkout customizer', 'Match': 'exact', 'Campaign': 'Review-variations', 'Reason': 'Irrelevant - triggered by customer feedback broad'},
        {'Keyword': 'customer accounts', 'Match': 'exact', 'Campaign': 'Review-variations', 'Reason': 'Irrelevant - triggered by customer feedback broad'},
        {'Keyword': 'product options', 'Match': 'broad', 'Campaign': 'Review-variations', 'Reason': 'Different product category'},
        {'Keyword': 'shipping rates', 'Match': 'broad', 'Campaign': 'Review-variations', 'Reason': 'Already added but verify active'},
        {'Keyword': 'free apps', 'Match': 'exact', 'Campaign': 'Review-variations', 'Reason': 'Low intent traffic'},
        {'Keyword': 'mobile app builder', 'Match': 'exact', 'Campaign': 'Review-variations', 'Reason': 'Different product'},
        {'Keyword': 'bundle apps', 'Match': 'exact', 'Campaign': 'Review-variations', 'Reason': 'Different product'},
        {'Keyword': 'product labels', 'Match': 'broad', 'Campaign': 'Review-variations', 'Reason': 'Different product category'},
    ]

    df_add_negatives = pd.DataFrame(additional_negatives)
    st.dataframe(df_add_negatives, use_container_width=True)

elif page == "Action Checklist":
    st.title("Action Checklist")
    st.markdown("### Priority Actions for Install Growth")

    st.subheader("IMMEDIATE ACTIONS (This Week)")

    actions_immediate = [
        ("PAUSE", "customer feedback (broad)", "Review-variations", "High CPI, low relevance"),
        ("PAUSE", "feedback app (broad)", "Review-variations", "Very low relevance"),
        ("PAUSE", "q&a (broad)", "Features", "High CPI, low volume"),
        ("INCREASE BID", "okendo to $5.00", "Competitors", "151.5% ROAS, best performer"),
        ("INCREASE BID", "yotpo reviews to $3.50", "Competitors", "341% ROAS"),
        ("INCREASE BID", "shopify product reviews to $2.00", "ProductReview", "Best CPI, underpriced"),
        ("ADD KEYWORD", "testimonials (exact)", "Review-variations", "321 installs from broad"),
        ("ADD KEYWORD", "loox reviews (exact)", "Competitors", "100 installs from broad"),
        ("ADD KEYWORD", "rating (exact)", "Review-variations", "77% install rate"),
    ]

    for action, keyword, campaign, reason in actions_immediate:
        if action == "PAUSE":
            st.checkbox(f"**{action}:** `{keyword}` in {campaign} - {reason}", key=f"imm_{keyword}")
        elif action == "INCREASE BID":
            st.checkbox(f"**{action}:** `{keyword}` in {campaign} - {reason}", key=f"imm_{keyword}")
        else:
            st.checkbox(f"**{action}:** `{keyword}` to {campaign} - {reason}", key=f"imm_{keyword}")

    st.markdown("---")

    st.subheader("SHORT-TERM ACTIONS (Next 2 Weeks)")

    actions_short = [
        "Add all HIGH priority new keywords (10 keywords)",
        "Reduce bid on google reviews/review to $3.50",
        "Reduce bid on carousel to $3.00",
        "Reduce bid on ugc to $4.00 or pause",
        "Add negative keywords: checkout customizer, customer accounts (exact)",
        "Add competitor keywords: stamped.io, fera reviews",
        "Increase bids on loox review, loox - photo reviews to $3.00",
    ]

    for action in actions_short:
        st.checkbox(action, key=f"short_{action[:20]}")

    st.markdown("---")

    st.subheader("ONGOING MONITORING")

    monitoring = [
        "Track CPI and install rate weekly",
        "Review search terms report bi-weekly for new opportunities",
        "Monitor competitor keyword performance",
        "Test MEDIUM priority keywords after HIGH priority launch",
        "Evaluate Features campaign ROI - consider budget reallocation to Competitors",
    ]

    for item in monitoring:
        st.info(item)

    st.markdown("---")

    st.subheader("Expected Outcomes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **From Pausing Underperformers:**
        - Save ~$200-300/month
        - Improve overall ROAS
        - Focus budget on converters
        """)

    with col2:
        st.markdown("""
        **From New Keywords:**
        - Est. 500-1000 additional installs/month
        - New competitor traffic capture
        - Better coverage of feature terms
        """)

# Footer
st.markdown("---")
st.caption("Judge.me Shopify Ads Analysis Dashboard | Generated February 2026 | Focus: Keyword Discovery for Install Growth")
