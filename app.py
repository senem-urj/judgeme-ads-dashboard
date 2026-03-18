"""
Judge.me Shopify App Store Ads Dashboard v2
P1: Aug 21, 2025 – Feb 18, 2026  (before keyword changes)
P2: Feb 24, 2026 – Mar 17, 2026  (after keyword changes, 22 days)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Judge.me Ads Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTH
# ============================================================================
def check_auth():
    if st.session_state.get("authenticated"):
        return True
    st.title("🔒 Judge.me Ads Dashboard")
    pw = st.text_input("Password:", type="password", key="login_pw")
    if st.button("Login", type="primary"):
        if pw == st.secrets.get("app_password", "judgeme2026"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.caption("Contact your team admin for access.")
    return False

# ============================================================================
# CONSTANTS
# ============================================================================
DATA_DIR = Path(__file__).parent / "data"

CAMPAIGN_MAP = {
    "Search_EN_ProductReview_2024.08.05": "ProductReview",
    "Search_EN_Competitors_2024.08.12": "Competitors",
    "Search_EN_Review-variations_2024.04.29": "Review-variations",
    "Search_EN_Features_2024.08.19": "Features",
    "Search_EN_Trust_2025.03.17": "Trust",
}

P1_FILES = [
    "p1_keywords_review_variations.csv",
    "p1_keywords_product_review.csv",
    "p1_keywords_competitors.csv",
    "p1_keywords_features.csv",
    "p1_keywords_trust.csv",
]
P2_FILES = [
    "p2_keywords_trust.csv",
    "p2_keywords_features.csv",
    "p2_keywords_competitors.csv",
    "p2_keywords_product_review.csv",
]
P2_SEARCH_FILES = [
    "p2_search_terms_trust.csv",
    "p2_search_terms_features.csv",
    "p2_search_terms_competitors.csv",
]

# Keywords where bids were increased in late Feb 2026
BID_INCREASED = {
    ("okendo", "exact"),
    ("yotpo reviews", "exact"),
    ("loox - photo reviews", "exact"),
    ("loox review", "exact"),
    ("shopify product reviews", "exact"),
    ("customer reviews", "exact"),
    ("reviews app", "exact"),
    ("review", "exact"),
    ("trustoo reviews", "exact"),
    ("rivo reviews", "exact"),
    ("reviews importer", "exact"),
    ("review importer", "exact"),
}

P1_LABEL = "Aug 21 – Feb 18 (P1)"
P2_LABEL = "Feb 24 – Mar 17 (P2)"

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_keywords(files):
    dfs = []
    for fname in files:
        p = DATA_DIR / fname
        if not p.exists():
            continue
        df = pd.read_csv(p)
        df["Campaign"] = df["Ad Name"].map(CAMPAIGN_MAP).fillna(df["Ad Name"])
        start = pd.to_datetime(df["Start Date"].iloc[0])
        end = pd.to_datetime(df["End Date"].iloc[0])
        df["_days"] = (end - start).days + 1
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    out = pd.concat(dfs, ignore_index=True)
    out = out.rename(columns={
        "Match Type": "Match",
        "Install Rate": "InstallRate",
        "Cost Per Install": "CPI",
        "Return On Spend": "ROAS",
        "Average Position": "AvgPos",
        "Click Through Rate": "CTR",
        "Cost Per Click": "CPC",
    })
    for c in ["Impressions", "Clicks", "Installs", "Spend", "Bid", "Customers", "Revenue"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    for c in ["CPI", "ROAS", "InstallRate", "AvgPos", "CTR", "CPC"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


@st.cache_data
def load_search_terms(files):
    dfs = []
    for fname in files:
        p = DATA_DIR / fname
        if not p.exists():
            continue
        df = pd.read_csv(p)
        df["Campaign"] = df["Ad Name"].map(CAMPAIGN_MAP).fillna(df["Ad Name"])
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    out = pd.concat(dfs, ignore_index=True)
    out = out.rename(columns={
        "Match Type": "Match",
        "Install Rate": "InstallRate",
        "Cost Per Install": "CPI",
        "Return On Spend": "ROAS",
    })
    for c in ["Impressions", "Clicks", "Installs", "Spend"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    for c in ["CPI", "ROAS", "InstallRate"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def build_comparison(p1, p2):
    """Merge P1 and P2 keyword data into a side-by-side comparison DataFrame."""
    def agg(df, prefix):
        g = df.groupby(["Keyword", "Match", "Campaign"], as_index=False).agg(
            Impressions=("Impressions", "sum"),
            Installs=("Installs", "sum"),
            Spend=("Spend", "sum"),
            Days=("_days", "first"),
            Bid=("Bid", "last"),
        )
        g["IPD"] = g["Installs"] / g["Days"]
        g["CPI"] = g.apply(lambda r: r.Spend / r.Installs if r.Installs > 0 else None, axis=1)
        return g.rename(columns={
            c: f"{prefix}_{c}" for c in ["Impressions", "Installs", "Spend", "Days", "Bid", "IPD", "CPI"]
        })

    a1 = agg(p1, "P1") if not p1.empty else pd.DataFrame()
    a2 = agg(p2, "P2") if not p2.empty else pd.DataFrame()

    if a1.empty or a2.empty:
        return pd.DataFrame()

    comp = pd.merge(a1, a2, on=["Keyword", "Match", "Campaign"], how="outer")

    # Identify which keywords were new vs existing vs bid-increased
    p1_keys = set(zip(p1["Keyword"].str.lower(), p1["Match"].str.lower()))
    p2_keys = set(zip(p2["Keyword"].str.lower(), p2["Match"].str.lower()))

    def get_status(row):
        kw = (str(row["Keyword"]).lower(), str(row["Match"]).lower())
        in_p1 = kw in p1_keys
        in_p2 = kw in p2_keys
        if in_p2 and not in_p1:
            return "New Keyword"
        if in_p1 and not in_p2:
            return "Not in P2"
        if kw in BID_INCREASED:
            return "Bid Increased"
        return "Existing"

    comp["Status"] = comp.apply(get_status, axis=1)

    # Fill numeric NaNs
    for c in ["P1_Impressions", "P1_Installs", "P1_Spend", "P1_IPD",
              "P2_Impressions", "P2_Installs", "P2_Spend", "P2_IPD"]:
        if c in comp.columns:
            comp[c] = comp[c].fillna(0)

    # Deltas
    comp["Delta_IPD"] = comp["P2_IPD"] - comp["P1_IPD"]
    comp["Delta_IPD_Pct"] = comp.apply(
        lambda r: (r["P2_IPD"] / r["P1_IPD"] - 1) * 100
        if (r["P1_IPD"] > 0 and pd.notna(r.get("P2_IPD")))
        else None,
        axis=1,
    )
    comp["Delta_CPI"] = comp.apply(
        lambda r: r["P2_CPI"] - r["P1_CPI"]
        if pd.notna(r.get("P1_CPI")) and pd.notna(r.get("P2_CPI"))
        else None,
        axis=1,
    )
    return comp


# ============================================================================
# HELPER: colour a delta value
# ============================================================================
def delta_arrow(val, invert=False):
    """Return a coloured string for a numeric delta."""
    if val is None or pd.isna(val):
        return "—"
    good = val > 0 if not invert else val < 0
    symbol = "▲" if val > 0 else "▼"
    color = "green" if good else "red"
    return f"<span style='color:{color}'>{symbol} {abs(val):.1f}</span>"


# ============================================================================
# PAGES
# ============================================================================

def page_before_after(p1, p2, comp):
    st.title("Before vs After: Impact of Keyword Changes")
    st.caption("Comparing daily install rates — P1 (181 days, pre-changes) vs P2 (22 days, post-changes)")

    if comp.empty:
        st.error("Comparison data not available.")
        return

    # ── Top metrics ──────────────────────────────────────────────────────────
    # Only compare campaigns present in both periods
    p2_campaigns = set(p2["Campaign"].unique())
    p1_comp = p1[p1["Campaign"].isin(p2_campaigns)]

    p1_ipd_total = p1_comp.groupby("Campaign").apply(
        lambda g: g["Installs"].sum() / g["_days"].iloc[0], include_groups=False
    ).sum()
    p2_ipd_total = p2.groupby("Campaign").apply(
        lambda g: g["Installs"].sum() / g["_days"].iloc[0], include_groups=False
    ).sum()

    p1_cpi_total = p1_comp["Spend"].sum() / p1_comp["Installs"].sum() if p1_comp["Installs"].sum() > 0 else 0
    p2_cpi_total = p2["Spend"].sum() / p2["Installs"].sum() if p2["Installs"].sum() > 0 else 0

    p1_spend_day = p1_comp.groupby("Campaign").apply(
        lambda g: g["Spend"].sum() / g["_days"].iloc[0], include_groups=False
    ).sum()
    p2_spend_day = p2.groupby("Campaign").apply(
        lambda g: g["Spend"].sum() / g["_days"].iloc[0], include_groups=False
    ).sum()

    new_kw_with_installs = comp[
        (comp["Status"] == "New Keyword") & (comp["P2_Installs"] > 0)
    ]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Installs / Day",
        f"{p2_ipd_total:.1f}",
        delta=f"{p2_ipd_total - p1_ipd_total:+.1f} vs P1 ({p1_ipd_total:.1f})",
        delta_color="normal",
    )
    c2.metric(
        "Avg CPI",
        f"${p2_cpi_total:.2f}",
        delta=f"{p2_cpi_total - p1_cpi_total:+.2f} vs P1 (${p1_cpi_total:.2f})",
        delta_color="inverse",
    )
    c3.metric(
        "Spend / Day",
        f"${p2_spend_day:.0f}",
        delta=f"{p2_spend_day - p1_spend_day:+.0f} vs P1 (${p1_spend_day:.0f})",
        delta_color="inverse",
    )
    c4.metric(
        "New KWs with Installs",
        f"{len(new_kw_with_installs)}",
        delta=f"{int(new_kw_with_installs['P2_Installs'].sum())} installs so far",
        delta_color="normal",
    )

    st.info(
        f"⚠️ **Note:** Review-variations campaign data not available for P2. "
        f"Comparison above excludes it from both periods for a fair apples-to-apples view."
    )

    st.markdown("---")

    # ── Campaign installs/day bar chart ──────────────────────────────────────
    st.subheader("Installs / Day by Campaign")

    camp_rows = []
    for camp in sorted(p2_campaigns):
        g1 = p1[p1["Campaign"] == camp]
        g2 = p2[p2["Campaign"] == camp]
        if not g1.empty:
            camp_rows.append({"Campaign": camp, "Period": P1_LABEL,
                               "Installs/Day": g1["Installs"].sum() / g1["_days"].iloc[0]})
        if not g2.empty:
            camp_rows.append({"Campaign": camp, "Period": P2_LABEL,
                               "Installs/Day": g2["Installs"].sum() / g2["_days"].iloc[0]})

    camp_df = pd.DataFrame(camp_rows)
    fig = px.bar(
        camp_df, x="Campaign", y="Installs/Day", color="Period", barmode="group",
        color_discrete_map={P1_LABEL: "#6c8ebf", P2_LABEL: "#82b366"},
        title="Daily install rate before vs after keyword changes",
    )
    fig.update_layout(yaxis_title="Installs per Day", legend_title="Period")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Keyword comparison table ──────────────────────────────────────────────
    st.subheader("Keyword-Level Comparison")

    status_filter = st.multiselect(
        "Filter by status:",
        ["Existing", "Bid Increased", "New Keyword", "Not in P2"],
        default=["Existing", "Bid Increased", "New Keyword"],
    )
    campaign_filter = st.multiselect(
        "Filter by campaign:",
        sorted(comp["Campaign"].dropna().unique()),
        default=sorted(comp["Campaign"].dropna().unique()),
    )

    view = comp[
        comp["Status"].isin(status_filter) & comp["Campaign"].isin(campaign_filter)
    ].copy()
    view = view.sort_values("P2_IPD", ascending=False)

    display_cols = {
        "Keyword": "Keyword",
        "Match": "Match",
        "Campaign": "Campaign",
        "Status": "Status",
        "P1_IPD": "P1 Installs/Day",
        "P2_IPD": "P2 Installs/Day",
        "Delta_IPD_Pct": "Change %",
        "P1_CPI": "P1 CPI",
        "P2_CPI": "P2 CPI",
        "P1_Bid": "P1 Bid",
        "P2_Bid": "P2 Bid",
    }
    disp = view[[c for c in display_cols if c in view.columns]].rename(columns=display_cols)

    for col in ["P1 Installs/Day", "P2 Installs/Day"]:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    for col in ["P1 CPI", "P2 CPI"]:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    for col in ["P1 Bid", "P2 Bid"]:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    if "Change %" in disp.columns:
        disp["Change %"] = disp["Change %"].apply(
            lambda x: f"+{x:.0f}%" if (pd.notna(x) and x > 0) else (f"{x:.0f}%" if pd.notna(x) else "NEW")
        )

    st.dataframe(disp, use_container_width=True)


def page_new_keywords(p1, p2, comp):
    st.title("New Keywords Status")
    st.caption("Keywords added after Feb 24, 2026 — how are they performing after 22 days?")

    if comp.empty:
        st.error("No data available.")
        return

    p1_keys = set(zip(p1["Keyword"].str.lower(), p1["Match"].str.lower()))
    new = p2[p2.apply(lambda r: (r["Keyword"].lower(), r["Match"].lower()) not in p1_keys, axis=1)].copy()

    if new.empty:
        st.info("No new keywords detected in P2.")
        return

    active = new[new["Installs"] > 0]
    getting_impressions = new[(new["Impressions"] > 0) & (new["Installs"] == 0)]
    dormant = new[new["Impressions"] == 0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total New Keywords", len(new))
    c2.metric("Getting Installs ✅", len(active), delta=f"{int(active['Installs'].sum())} installs total")
    c3.metric("Impressions, No Installs ⚠️", len(getting_impressions))
    c4.metric("Zero Impressions ❌", len(dormant))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["✅ Getting Installs", "⚠️ Getting Impressions Only", "❌ Zero Impressions"])

    with tab1:
        if active.empty:
            st.info("No new keywords with installs yet.")
        else:
            d = active[["Campaign", "Keyword", "Match", "Bid", "Impressions", "Installs", "Spend", "CPI", "InstallRate"]].copy()
            d["CPI"] = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
            d["InstallRate"] = d["InstallRate"].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "—")
            d["Spend"] = d["Spend"].apply(lambda x: f"${x:.0f}")
            d["Bid"] = d["Bid"].apply(lambda x: f"${x:.2f}")
            d = d.sort_values("Installs", ascending=False)
            st.dataframe(d, use_container_width=True)

            st.subheader("Installs by New Keyword")
            fig = px.bar(
                active.sort_values("Installs", ascending=True),
                x="Installs", y="Keyword", orientation="h",
                color="Campaign", title="New keywords ranked by installs (22 days)",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if getting_impressions.empty:
            st.info("No keywords in this state.")
        else:
            d = getting_impressions[["Campaign", "Keyword", "Match", "Bid", "Impressions", "Clicks"]].copy()
            d["Bid"] = d["Bid"].apply(lambda x: f"${x:.2f}")
            st.dataframe(d.sort_values("Impressions", ascending=False), use_container_width=True)
            st.warning("These keywords are showing but not converting — may need better ad copy or lower bid expectations.")

    with tab3:
        if dormant.empty:
            st.info("All new keywords are getting impressions!")
        else:
            d = dormant[["Campaign", "Keyword", "Match", "Bid", "Status"]].copy() if "Status" in dormant.columns else dormant[["Campaign", "Keyword", "Match", "Bid"]].copy()
            d["Bid"] = d["Bid"].apply(lambda x: f"${x:.2f}")
            d = d.sort_values(["Campaign", "Bid"], ascending=[True, False])
            st.dataframe(d, use_container_width=True)
            st.error(
                "Zero impressions after 22 days = bids too low to win any auctions. "
                "Either raise bids to $2.50–$3.00 minimum, or these terms have very low search volume."
            )


def page_bid_impact(comp):
    st.title("Bid Increase Impact")
    st.caption("12 keywords had their bids raised — here's what changed.")

    if comp.empty:
        st.error("No comparison data available.")
        return

    bid_df = comp[comp["Status"] == "Bid Increased"].copy()

    if bid_df.empty:
        st.info("No bid-increased keywords found in data.")
        return

    # Summary metrics
    improved = bid_df[bid_df["Delta_IPD"] > 0]
    declined = bid_df[bid_df["Delta_IPD"] < 0]
    avg_cpi_increase = bid_df["Delta_CPI"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Keywords with Bid Increase", len(bid_df))
    c2.metric("Volume Improved ✅", len(improved))
    c3.metric("Volume Declined ❌", len(declined))
    c4.metric(
        "Avg CPI Change",
        f"+${avg_cpi_increase:.2f}" if pd.notna(avg_cpi_increase) else "—",
        delta="higher cost per install",
        delta_color="inverse",
    )

    st.markdown("---")

    # Side-by-side bar chart: installs/day before vs after
    chart_data = []
    for _, r in bid_df.iterrows():
        chart_data.append({"Keyword": r["Keyword"], "Period": P1_LABEL, "Installs/Day": r["P1_IPD"]})
        chart_data.append({"Keyword": r["Keyword"], "Period": P2_LABEL, "Installs/Day": r["P2_IPD"]})

    chart_df = pd.DataFrame(chart_data)
    chart_df = chart_df.sort_values(
        "Installs/Day",
        ascending=True,
    )

    fig = px.bar(
        chart_df,
        x="Installs/Day",
        y="Keyword",
        color="Period",
        barmode="group",
        orientation="h",
        color_discrete_map={P1_LABEL: "#6c8ebf", P2_LABEL: "#82b366"},
        title="Installs per day — before vs after bid increase",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Detail Table")

    d = bid_df[[
        "Keyword", "Match", "Campaign",
        "P1_Bid", "P2_Bid",
        "P1_IPD", "P2_IPD", "Delta_IPD_Pct",
        "P1_CPI", "P2_CPI", "Delta_CPI",
    ]].copy().sort_values("Delta_IPD_Pct", ascending=False)

    d["P1_Bid"] = d["P1_Bid"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    d["P2_Bid"] = d["P2_Bid"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    d["P1_IPD"] = d["P1_IPD"].apply(lambda x: f"{x:.2f}")
    d["P2_IPD"] = d["P2_IPD"].apply(lambda x: f"{x:.2f}")
    d["Delta_IPD_Pct"] = d["Delta_IPD_Pct"].apply(
        lambda x: f"+{x:.0f}%" if (pd.notna(x) and x > 0) else (f"{x:.0f}%" if pd.notna(x) else "—")
    )
    d["P1_CPI"] = d["P1_CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    d["P2_CPI"] = d["P2_CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    d["Delta_CPI"] = d["Delta_CPI"].apply(
        lambda x: f"+${x:.2f}" if (pd.notna(x) and x > 0) else (f"${x:.2f}" if pd.notna(x) else "—")
    )

    d = d.rename(columns={
        "P1_Bid": "Old Bid", "P2_Bid": "New Bid",
        "P1_IPD": "P1 Installs/Day", "P2_IPD": "P2 Installs/Day",
        "Delta_IPD_Pct": "Volume Δ",
        "P1_CPI": "P1 CPI", "P2_CPI": "P2 CPI", "Delta_CPI": "CPI Δ",
    })
    st.dataframe(d, use_container_width=True)

    st.markdown("---")
    st.subheader("Interpretation")
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Working well (increase volume without huge CPI penalty):**")
        st.markdown("""
- `shopify product reviews` — **+195%** volume, CPI went $1.16 → $2.24 (still cheap)
- `trustoo reviews` — **+338%** (small volume but confirmed it's alive)
- `yotpo reviews` — **+136%** (small volume)
- `review` (exact) — **+21%** at massive scale (17→21/day = 3.7 extra installs/day)
- `reviews importer` — **+83%** volume
- `review importer` — **+69%** volume
""")
    with col2:
        st.error("**Unexpected declines — investigate:**")
        st.markdown("""
- `loox - photo reviews` — **disappeared** (was 0.09/day, now 0)
- `rivo reviews` — **disappeared** (was 0.14/day, now 0)
- `customer reviews` — **-54%** (was 0.40/day, now 0.18/day)
- `loox review` — **-40%** (was 0.46/day, now 0.27/day)

These may be losing auctions to competitors at the higher bid level, or budget is being reallocated internally. Consider lowering bids back slightly to test.
""")


def page_recommendations(p1, p2, comp, search_df):
    st.title("Data-Driven Recommendations")
    st.caption("Based on 22 days of post-change data (Feb 24 – Mar 17, 2026)")

    st.markdown("---")

    # ── SECTION 1: Pause ──────────────────────────────────────────────────────
    st.subheader("🔴 Pause These Keywords Now")
    st.markdown("Confirmed underperformers — 22 days of data is enough to act.")

    pause_data = [
        {
            "Keyword": "carousel", "Match": "broad", "Campaign": "Features",
            "P2 CPI": "$19.50", "P2 Installs": 4, "P2 Spend": "$78",
            "Reason": "Highest CPI in entire account. 22 days, 4 installs. Stop.",
        },
        {
            "Keyword": "q&a", "Match": "broad", "Campaign": "Features",
            "P2 CPI": "—", "P2 Installs": 0, "P2 Spend": "$12",
            "Reason": "Zero installs. Always been bad. Confirmed waste.",
        },
        {
            "Keyword": "rich snippet", "Match": "broad", "Campaign": "Features",
            "P2 CPI": "—", "P2 Installs": 0, "P2 Spend": "$5",
            "Reason": "Zero installs both periods. The term doesn't convert.",
        },
        {
            "Keyword": "question", "Match": "broad", "Campaign": "Trust",
            "P2 CPI": "—", "P2 Installs": 0, "P2 Spend": "$16",
            "Reason": "Zero installs on 74 impressions. 0% install rate.",
        },
        {
            "Keyword": "google reviews", "Match": "exact", "Campaign": "ProductReview",
            "P2 CPI": "$9.11", "P2 Installs": 45, "P2 Spend": "$410",
            "Reason": "3× the account avg CPI. High spend, low return. Still burning $19/day.",
        },
        {
            "Keyword": "google review", "Match": "exact", "Campaign": "ProductReview",
            "P2 CPI": "$8.61", "P2 Installs": 18, "P2 Spend": "$155",
            "Reason": "Same story as 'google reviews'. High CPI, confirmed across both periods.",
        },
    ]
    st.dataframe(pd.DataFrame(pause_data), use_container_width=True)

    pause_spend = 78 + 12 + 5 + 16 + 410 + 155
    pause_daily = round(pause_spend / 22)
    st.error(
        f"💸 Pausing these 6 keywords frees up ~**${pause_daily}/day** "
        f"(${pause_spend} spent in 22 days) to reallocate to what's working."
    )

    st.markdown("---")

    # ── SECTION 2: Scale Winners ───────────────────────────────────────────────
    st.subheader("🟢 Scale These — They're Working")

    scale_data = [
        {
            "Keyword": "shopify product reviews", "Match": "exact", "Campaign": "ProductReview",
            "Action": "Increase bid $2.00 → $2.50",
            "Why": "+195% installs after bid increase. CPI still only $2.24. Best ROI of all bid changes.",
        },
        {
            "Keyword": "review widget", "Match": "broad", "Campaign": "ProductReview",
            "Action": "Increase bid $4.00 → $5.00",
            "Why": "111 installs in 22 days. This keyword didn't exist in P1. Prove it scales.",
        },
        {
            "Keyword": "stars", "Match": "broad", "Campaign": "Trust",
            "Action": "Increase bid $5.00 → $7.00",
            "Why": "84% install rate — highest in the Trust campaign. Only 264 impressions. Much more headroom.",
        },
        {
            "Keyword": "review", "Match": "exact", "Campaign": "ProductReview",
            "Action": "Consider bid $2.00 → $2.50",
            "Why": "+21% volume after last increase. At 21 installs/day, even +2/day is significant.",
        },
        {
            "Keyword": "loox reviews", "Match": "exact", "Campaign": "Competitors",
            "Action": "Increase bid $3.50 → $4.50",
            "Why": "New keyword, 10 installs in 22 days at $4.55 CPI. Signal is positive, increase budget.",
        },
    ]
    st.dataframe(pd.DataFrame(scale_data), use_container_width=True)

    st.markdown("---")

    # ── SECTION 3: Fix Low-Bid Dormant Keywords ────────────────────────────────
    st.subheader("🟡 Fix Dormant Keywords (Bids Too Low)")
    st.markdown(
        "Many new competitor keywords were added at **$1.00 bid** and have zero impressions. "
        "At $1 you can't win any auctions. Either raise them or accept they won't run."
    )

    p1_keys = set(zip(p1["Keyword"].str.lower(), p1["Match"].str.lower()))
    dormant_low = p2[
        (p2["Impressions"] == 0) &
        (p2["Bid"] <= 1.5) &
        p2.apply(lambda r: (r["Keyword"].lower(), r["Match"].lower()) not in p1_keys, axis=1)
    ].copy()

    if not dormant_low.empty:
        st.markdown(f"**{len(dormant_low)} keywords at ≤$1.50 bid with zero impressions.**")
        d = dormant_low[["Campaign", "Keyword", "Match", "Bid"]].copy()
        d["Bid"] = d["Bid"].apply(lambda x: f"${x:.2f}")
        d["Recommendation"] = "Raise to $2.50 or pause if low-priority"
        st.dataframe(d.sort_values(["Campaign", "Keyword"]), use_container_width=True)

    st.markdown("---")

    # ── SECTION 4: Search Term Opportunities ──────────────────────────────────
    st.subheader("🔵 New Search Term Opportunities (P2)")

    if not search_df.empty:
        # Find search terms not yet in keyword list
        p2_keywords = set(p2["Keyword"].str.lower())
        opp = search_df[
            (~search_df["Search Term"].str.lower().isin(p2_keywords)) &
            (search_df["Installs"] >= 3)
        ].copy()

        if not opp.empty:
            cols = [c for c in ["Campaign", "Search Term", "Keyword", "Match", "Impressions", "Installs", "CPI", "InstallRate"] if c in opp.columns]
            opp_disp = opp[cols].copy()
            if "CPI" in opp_disp.columns:
                opp_disp["CPI"] = opp_disp["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
            if "InstallRate" in opp_disp.columns:
                opp_disp["InstallRate"] = opp_disp["InstallRate"].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "—")
            opp_disp = opp_disp.sort_values("Installs", ascending=False)
            st.markdown("Search terms generating installs that aren't yet exact match keywords:")
            st.dataframe(opp_disp, use_container_width=True)
        else:
            st.info("No new high-volume search term opportunities identified.")
    else:
        st.info("Search term data not available.")

    st.markdown("---")

    # ── SECTION 5: Budget Reallocation Summary ────────────────────────────────
    st.subheader("💰 Budget Reallocation Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Free up (pause underperformers):**")
        st.markdown(f"~${pause_daily}/day from 6 keywords to pause")
    with col2:
        st.markdown("**Reallocate to (scale winners):**")
        st.markdown("""
- `shopify product reviews` (+$0.50 bid)
- `review widget broad` (+$1.00 bid)
- `stars broad` in Trust (+$2.00 bid)
- `loox reviews` exact (+$1.00 bid)
""")


def page_keyword_analysis(p2):
    st.title("Keyword Analysis — Current Period")
    st.caption(f"P2: Feb 24 – Mar 17, 2026 (22 days)")

    if p2.empty:
        st.error("No P2 data available.")
        return

    campaign = st.selectbox("Campaign:", sorted(p2["Campaign"].unique()))
    df = p2[p2["Campaign"] == campaign].copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Keywords", len(df))
    c2.metric("Installs", f"{int(df['Installs'].sum()):,}")
    c3.metric("Spend", f"${df['Spend'].sum():,.0f}")
    avg_cpi = df["Spend"].sum() / df["Installs"].sum() if df["Installs"].sum() > 0 else 0
    c4.metric("Avg CPI", f"${avg_cpi:.2f}")

    df_disp = df[["Keyword", "Match", "Bid", "Impressions", "Installs", "Spend", "CPI", "InstallRate"]].copy()
    df_disp["Bid"] = df_disp["Bid"].apply(lambda x: f"${x:.2f}")
    df_disp["Spend"] = df_disp["Spend"].apply(lambda x: f"${x:.0f}")
    df_disp["CPI"] = df_disp["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    df_disp["InstallRate"] = df_disp["InstallRate"].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "—")
    df_disp = df_disp.sort_values("Installs", ascending=False)
    st.dataframe(df_disp, use_container_width=True)

    if df["Installs"].sum() > 0:
        st.subheader("CPI vs Installs")
        fig = px.scatter(
            df[df["Installs"] > 0],
            x="CPI", y="Installs",
            size="Spend", color="InstallRate",
            hover_name="Keyword",
            color_continuous_scale="RdYlGn",
            title="Bubble size = spend | colour = install rate",
        )
        st.plotly_chart(fig, use_container_width=True)


def page_search_terms(search_df):
    st.title("Search Term Opportunities — P2")
    st.caption("What people are actually searching when they see your ads (Feb 24 – Mar 17)")

    if search_df.empty:
        st.error("Search term data not available.")
        return

    campaign = st.selectbox(
        "Campaign:",
        ["All"] + sorted(search_df["Campaign"].dropna().unique()),
    )
    df = search_df if campaign == "All" else search_df[search_df["Campaign"] == campaign]
    df = df[df["Installs"] > 0].sort_values("Installs", ascending=False)

    if df.empty:
        st.info("No search terms with installs found.")
        return

    cols = [c for c in ["Campaign", "Search Term", "Keyword", "Match", "Impressions", "Installs", "Spend", "CPI", "InstallRate"] if c in df.columns]
    d = df[cols].copy()
    if "CPI" in d.columns:
        d["CPI"] = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    if "InstallRate" in d.columns:
        d["InstallRate"] = d["InstallRate"].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "—")
    if "Spend" in d.columns:
        d["Spend"] = d["Spend"].apply(lambda x: f"${x:.0f}")
    st.dataframe(d, use_container_width=True)


def page_negative_keywords():
    st.title("Negative Keywords")

    neg_data = {
        "ProductReview": [
            "judge.me (broad)", "judge me (broad)", "loox", "trustoo", "yotpo",
            "okendo", "rivo", "trustpilot",
        ],
        "Review-variations": [
            "judge (broad)", "Google Reviews (broad + exact)", "ali review (broad)",
            "amazon review (broad)", "etsy reviews (broad)", "testimonials slider (exact)",
        ],
        "Features": ["judge.me branded terms", "competitor names", "reviews (exact)"],
        "Trust": ["trustpilot", "trust pilot", "social media icons"],
    }

    for camp, kws in neg_data.items():
        with st.expander(f"**{camp}** ({len(kws)} entries)"):
            for kw in kws:
                st.markdown(f"- {kw}")


def page_action_checklist(comp, p2):
    st.title("Action Checklist")
    st.caption("Priority actions based on P2 data")

    st.subheader("🔴 Immediate (This Week)")
    immediate = [
        ("PAUSE", "google reviews (exact)", "ProductReview", "CPI $9.11, confirmed 2 periods"),
        ("PAUSE", "google review (exact)", "ProductReview", "CPI $8.61, confirmed 2 periods"),
        ("PAUSE", "carousel (broad)", "Features", "CPI $19.50, 4 installs in 22 days"),
        ("PAUSE", "q&a (broad)", "Features", "Zero installs both periods"),
        ("PAUSE", "rich snippet (broad)", "Features", "Zero installs both periods"),
        ("PAUSE", "question (broad)", "Trust", "Zero installs on 74 impressions"),
        ("INCREASE BID $2.00→$2.50", "shopify product reviews", "ProductReview", "Best bid increase result (+195%)"),
        ("INCREASE BID $4.00→$5.00", "review widget (broad)", "ProductReview", "111 installs/22 days, scaling well"),
        ("INCREASE BID $5.00→$7.00", "stars (broad)", "Trust", "84% install rate, needs more impressions"),
    ]
    for action, kw, camp, note in immediate:
        st.checkbox(f"**{action}** `{kw}` ({camp}) — {note}", key=f"imm_{kw}")

    st.markdown("---")
    st.subheader("🟡 Short-Term (Next 2 Weeks)")
    short = [
        "Raise all $1.00-bid Competitors keywords to $2.50 minimum or pause them",
        "Increase loox reviews (exact) bid $3.50→$4.50 — showing early traction",
        "Add review (exact) bid increase: $2.00→$2.50 (test — already +21% from last increase)",
        "Investigate why loox review / customer reviews / rivo reviews declined after bid increase",
        "Download Review-variations campaign data for P2 (missing from current dataset)",
    ]
    for a in short:
        st.checkbox(a, key=f"short_{a[:30]}")

    st.markdown("---")
    st.subheader("🟢 Ongoing Monitoring")
    st.markdown("""
- Review Trust campaign weekly — `stars` and `comments` are new and early-stage
- Check if `aliexpress reviews` (exact, $4.00) scales beyond 5 installs
- In 4 weeks re-evaluate `review importer` and `reviews importer` — both showing improving daily rates
""")


# ============================================================================
# MAIN
# ============================================================================

if not check_auth():
    st.stop()

# Load data
p1 = load_keywords(P1_FILES)
p2 = load_keywords(P2_FILES)
search_p2 = load_search_terms(P2_SEARCH_FILES)
comp = build_comparison(p1, p2)

# Sidebar
st.sidebar.title("⭐ Judge.me Ads")
st.sidebar.markdown(f"**P1:** Aug 21 – Feb 18, 2026 (181 days)")
st.sidebar.markdown(f"**P2:** Feb 24 – Mar 17, 2026 (22 days)")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate:",
    [
        "📊 Before vs After",
        "🆕 New Keywords Status",
        "💸 Bid Change Impact",
        "📋 Keyword Analysis",
        "🔍 Search Terms (P2)",
        "💡 Recommendations",
        "🚫 Negative Keywords",
        "✅ Action Checklist",
    ],
)

st.sidebar.markdown("---")
if not p1.empty:
    st.sidebar.caption(f"P1 keywords loaded: {len(p1)}")
if not p2.empty:
    st.sidebar.caption(f"P2 keywords loaded: {len(p2)}")
if not search_p2.empty:
    st.sidebar.caption(f"P2 search terms loaded: {len(search_p2)}")

# Route
if page == "📊 Before vs After":
    page_before_after(p1, p2, comp)
elif page == "🆕 New Keywords Status":
    page_new_keywords(p1, p2, comp)
elif page == "💸 Bid Change Impact":
    page_bid_impact(comp)
elif page == "📋 Keyword Analysis":
    page_keyword_analysis(p2)
elif page == "🔍 Search Terms (P2)":
    page_search_terms(search_p2)
elif page == "💡 Recommendations":
    page_recommendations(p1, p2, comp, search_p2)
elif page == "🚫 Negative Keywords":
    page_negative_keywords()
elif page == "✅ Action Checklist":
    page_action_checklist(comp, p2)

st.markdown("---")
st.caption("Judge.me Ads Dashboard v2 · P1: Aug 21–Feb 18, 2026 · P2: Feb 24–Mar 17, 2026")
