"""
Judge.me Shopify App Store Ads Dashboard v4
Generic paid ads performance dashboard with trend analysis,
audience splits, keyword intelligence, change log, and diagnosis.

Data coverage:
  Full Year: Apr 7, 2025 – Apr 7, 2026 (campaign aggregate)
  Daily: Aug 21, 2025 – Apr 15, 2026 (keyword + bid detail)
  P2: Feb 24, 2026 – Mar 17, 2026 (22 days, keyword detail)
  P3: Jan 16, 2026 – Apr 15, 2026 (aggregate incl. language campaigns)
  Q1 2026: Jan 8, 2026 – Apr 7, 2026 (90 days, search term detail)
  Change Log: Feb 24, 2026 + Mar 18–Apr 15, 2026 (159 events)
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
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 18px; }
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
    "Search_EN_BrandProtection_2024.10.08": "BrandProtection",
    "Search_EN_PLUS_ProductReview_2024.12.31": "PLUS-ProductReview",
    "Search_PT_Generic_2025.03.17": "PT-Generic",
    "Search_EN_Exploration_SEO_2025.03.10": "Exploration-SEO",
    "Search_EN_Exploration_Instagram_03.09.2025": "Exploration-Instagram",
    "Placement_Home_2025.11.17": "Placement-Home",
    "AERI_KWs_Exploration_18.08.2025": "AERI-Exploration",
}

CAMPAIGN_COLORS = {
    "ProductReview":        "#4C78A8",
    "Competitors":          "#F58518",
    "Review-variations":    "#E45756",
    "Features":             "#72B7B2",
    "Trust":                "#54A24B",
    "BrandProtection":      "#B279A2",
    "PLUS-ProductReview":   "#FF9DA7",
    "PT-Generic":           "#9D755D",
    "Exploration-SEO":      "#BAB0AC",
    "Exploration-Instagram":"#EDC948",
    "Placement-Home":       "#76B7B2",
    "AERI-Exploration":     "#59A14F",
}

BID_INCREASED = {
    ("okendo", "exact"), ("yotpo reviews", "exact"),
    ("loox - photo reviews", "exact"), ("loox review", "exact"),
    ("shopify product reviews", "exact"), ("customer reviews", "exact"),
    ("reviews app", "exact"), ("review", "exact"),
    ("trustoo reviews", "exact"), ("rivo reviews", "exact"),
    ("reviews importer", "exact"), ("review importer", "exact"),
}

P1_LABEL = "P1 (Aug 21–Feb 18)"
P2_LABEL = "P2 (Feb 24–Mar 17)"

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_daily():
    p = DATA_DIR / "daily_metrics.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Campaign"] = df["Campaign Name"].map(CAMPAIGN_MAP).fillna(df["Campaign Name"])
    for c in ["Impressions","Clicks","Installs","Spend","Customers","Revenue"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_year_campaigns():
    p = DATA_DIR / "year_campaign_metrics.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df["Campaign"] = df["Ad Name"].map(CAMPAIGN_MAP).fillna(df["Ad Name"])
    for c in ["Impressions","Clicks","Installs","Spend","Customers","Revenue",
              "Cost Per Install","Return On Spend","Daily Budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

@st.cache_data
def load_p2_campaigns():
    p = DATA_DIR / "p2_campaign_metrics.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df["Campaign"] = df["Ad Name"].map(CAMPAIGN_MAP).fillna(df["Ad Name"])
    for c in ["Impressions","Clicks","Installs","Spend","Customers","Revenue",
              "Cost Per Install","Return On Spend","Daily Budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

@st.cache_data
def load_keywords(period):
    """period: 'p1' or 'p2'"""
    p = DATA_DIR / f"keywords_{period}.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df["Campaign"] = df["Ad Name"].map(CAMPAIGN_MAP).fillna(df["Ad Name"])
    start = pd.to_datetime(df["Start Date"].iloc[0])
    end = pd.to_datetime(df["End Date"].iloc[0])
    df["_days"] = (end - start).days + 1
    df = df.rename(columns={
        "Match Type":"Match","Install Rate":"InstallRate",
        "Cost Per Install":"CPI","Return On Spend":"ROAS",
        "Average Position":"AvgPos","Click Through Rate":"CTR","Cost Per Click":"CPC",
    })
    for c in ["Impressions","Clicks","Installs","Spend","Bid"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    for c in ["CPI","ROAS","InstallRate","AvgPos","CTR","CPC"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

@st.cache_data
def load_splits(fname):
    p = DATA_DIR / fname
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["Impressions","Clicks","Installs","Spend","Customers","Revenue"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_search_terms():
    p = DATA_DIR / "q1_search_terms_agg.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["Impressions","Clicks","Installs","Spend","Customers","Revenue"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_changelog():
    p = DATA_DIR / "keyword_changelog.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    if "P2 Installs" in df.columns:
        df["P2 Installs"] = pd.to_numeric(df["P2 Installs"], errors="coerce").fillna(0).astype(int)
    return df

def build_kw_comparison(p1, p2):
    if p1.empty or p2.empty:
        return pd.DataFrame()

    def agg(df, prefix):
        g = df.groupby(["Keyword","Match","Campaign"], as_index=False).agg(
            Impressions=("Impressions","sum"), Installs=("Installs","sum"),
            Spend=("Spend","sum"), Days=("_days","first"), Bid=("Bid","last"),
        )
        g["IPD"] = g["Installs"] / g["Days"]
        g["CPI"] = g.apply(lambda r: r.Spend / r.Installs if r.Installs > 0 else None, axis=1)
        return g.rename(columns={c: f"{prefix}_{c}" for c in ["Impressions","Installs","Spend","Days","Bid","IPD","CPI"]})

    a1, a2 = agg(p1, "P1"), agg(p2, "P2")
    comp = pd.merge(a1, a2, on=["Keyword","Match","Campaign"], how="outer")

    p1_keys = set(zip(p1["Keyword"].str.lower(), p1["Match"].str.lower()))
    p2_keys = set(zip(p2["Keyword"].str.lower(), p2["Match"].str.lower()))

    def get_status(row):
        kw = (str(row["Keyword"]).lower(), str(row["Match"]).lower())
        in_p1, in_p2 = kw in p1_keys, kw in p2_keys
        if in_p2 and not in_p1: return "New in P2"
        if in_p1 and not in_p2: return "Dropped in P2"
        if kw in BID_INCREASED: return "Bid Increased"
        return "Unchanged"

    comp["Status"] = comp.apply(get_status, axis=1)
    for c in ["P1_Impressions","P1_Installs","P1_Spend","P1_IPD","P2_Impressions","P2_Installs","P2_Spend","P2_IPD"]:
        if c in comp.columns:
            comp[c] = comp[c].fillna(0)
    comp["Delta_IPD"] = comp["P2_IPD"] - comp["P1_IPD"]
    comp["Delta_IPD_Pct"] = comp.apply(
        lambda r: (r["P2_IPD"] / r["P1_IPD"] - 1) * 100
        if r["P1_IPD"] > 0 and pd.notna(r.get("P2_IPD")) else None, axis=1)
    comp["Delta_CPI"] = comp.apply(
        lambda r: r["P2_CPI"] - r["P1_CPI"]
        if pd.notna(r.get("P1_CPI")) and pd.notna(r.get("P2_CPI")) else None, axis=1)
    return comp

# ============================================================================
# PAGES
# ============================================================================

def page_overview(daily, yr_camps, p2_camps):
    st.title("📈 Performance Overview")

    # ── Full-year KPIs ────────────────────────────────────────────────────────
    if not yr_camps.empty:
        jm = yr_camps[yr_camps["App Name"] == "Judge.me Product Reviews App"]
        yr_installs = jm["Installs"].sum()
        yr_spend    = jm["Spend"].sum()
        yr_cust     = jm["Customers"].sum()
        yr_rev      = jm["Revenue"].sum()
        yr_cpi      = yr_spend / yr_installs if yr_installs > 0 else 0
        yr_roas     = yr_rev / yr_spend * 100 if yr_spend > 0 else 0
    else:
        yr_installs = yr_spend = yr_cust = yr_rev = yr_cpi = yr_roas = 0

    st.subheader("Full Year: Apr 7, 2025 – Apr 7, 2026")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Installs",    f"{int(yr_installs):,}")
    c2.metric("Total Spend",       f"${yr_spend:,.0f}")
    c3.metric("Avg CPI",           f"${yr_cpi:.2f}")
    c4.metric("Total Customers",   f"{int(yr_cust):,}")
    c5.metric("Total Revenue",     f"${yr_rev:,.0f}")
    c6.metric("ROAS",              f"{yr_roas:.0f}%")

    st.markdown("---")

    # ── P1 vs P2 snapshot ────────────────────────────────────────────────────
    st.subheader("Before vs After the Feb 24 Changes")
    st.caption("P1: Aug 21–Feb 18, 2026 (181 days) · P2: Feb 24–Mar 17, 2026 (22 days)")

    if not daily.empty:
        p1_inst  = daily["Installs"].sum()
        p1_spend = daily["Spend"].sum()
        p1_cust  = daily["Customers"].sum()
        p1_rev   = daily["Revenue"].sum()
        p1_ipd   = p1_inst / 181
        p1_cpi   = p1_spend / p1_inst if p1_inst > 0 else 0
        p1_roas  = p1_rev / p1_spend * 100 if p1_spend > 0 else 0
        p1_conv  = p1_cust / p1_inst * 100 if p1_inst > 0 else 0
    else:
        p1_inst = p1_spend = p1_cust = p1_rev = p1_ipd = p1_cpi = p1_roas = p1_conv = 0

    if not p2_camps.empty:
        p2_inst  = p2_camps["Installs"].sum()
        p2_spend = p2_camps["Spend"].sum()
        p2_cust  = p2_camps["Customers"].sum()
        p2_rev   = p2_camps["Revenue"].sum()
        p2_ipd   = p2_inst / 22
        p2_cpi   = p2_spend / p2_inst if p2_inst > 0 else 0
        p2_roas  = p2_rev / p2_spend * 100 if p2_spend > 0 else 0
        p2_conv  = p2_cust / p2_inst * 100 if p2_inst > 0 else 0
    else:
        p2_inst = p2_spend = p2_cust = p2_rev = p2_ipd = p2_cpi = p2_roas = p2_conv = 0

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{P1_LABEL}**")
        a, b, c, d = st.columns(4)
        a.metric("Installs/Day", f"{p1_ipd:.1f}")
        b.metric("CPI",          f"${p1_cpi:.2f}")
        c.metric("Conv %",       f"{p1_conv:.1f}%")
        d.metric("ROAS",         f"{p1_roas:.0f}%")
    with col2:
        st.markdown(f"**{P2_LABEL}**")
        a, b, c, d = st.columns(4)
        a.metric("Installs/Day", f"{p2_ipd:.1f}",  delta=f"{p2_ipd-p1_ipd:+.1f}")
        b.metric("CPI",          f"${p2_cpi:.2f}", delta=f"{p2_cpi-p1_cpi:+.2f}", delta_color="inverse")
        c.metric("Conv %",       f"{p2_conv:.1f}%",delta=f"{p2_conv-p1_conv:+.1f}pp")
        d.metric("ROAS",         f"{p2_roas:.1f}%",delta=f"{p2_roas-p1_roas:.0f}pp", delta_color="normal")

    if p1_conv > 0:
        st.warning(
            f"⚠️ **Install volume is stable** ({p1_ipd:.0f} → {p2_ipd:.0f} installs/day), "
            f"but install→customer conversion dropped **{p1_conv:.1f}% → {p2_conv:.1f}%** "
            f"and ROAS fell **{p1_roas:.0f}% → {p2_roas:.1f}%**. "
            f"The issue is **traffic quality**, not reach. See the Diagnosis page for actions."
        )

    st.markdown("---")

    # ── Monthly trend ────────────────────────────────────────────────────────
    if not daily.empty:
        st.subheader("Monthly Performance Trend (P1 Daily Data)")
        daily["Month"] = daily["Date"].dt.to_period("M").astype(str)
        mo = daily.groupby("Month").agg(
            Installs=("Installs","sum"), Spend=("Spend","sum"),
            Customers=("Customers","sum"), Revenue=("Revenue","sum"),
        ).reset_index()
        mo["CPI"]      = mo["Spend"] / mo["Installs"]
        mo["ROAS_pct"] = mo["Revenue"] / mo["Spend"] * 100
        mo["Conv_pct"] = mo["Customers"] / mo["Installs"] * 100

        # append P2 row
        if p2_inst > 0:
            mo = pd.concat([mo, pd.DataFrame([{
                "Month":"2026-P2","Installs":p2_inst,"Spend":p2_spend,
                "Customers":p2_cust,"Revenue":p2_rev,
                "CPI":p2_cpi,"ROAS_pct":p2_roas,"Conv_pct":p2_conv,
            }])], ignore_index=True)

        t1, t2, t3 = st.tabs(["Installs & Spend","ROAS & Revenue","Conversion Rate"])
        with t1:
            fig = go.Figure()
            fig.add_bar(x=mo["Month"], y=mo["Installs"], name="Installs", marker_color="#4C78A8")
            fig.add_scatter(x=mo["Month"], y=mo["Spend"], name="Spend ($)", yaxis="y2",
                            line=dict(color="#F58518", width=2), mode="lines+markers")
            fig.update_layout(yaxis=dict(title="Installs"),
                              yaxis2=dict(title="Spend ($)", overlaying="y", side="right"),
                              legend=dict(orientation="h"), height=340)
            st.plotly_chart(fig, use_container_width=True)
        with t2:
            fig = go.Figure()
            fig.add_bar(x=mo["Month"], y=mo["Revenue"], name="Revenue ($)", marker_color="#54A24B")
            fig.add_scatter(x=mo["Month"], y=mo["ROAS_pct"], name="ROAS (%)", yaxis="y2",
                            line=dict(color="#E45756", width=2), mode="lines+markers")
            fig.update_layout(yaxis=dict(title="Revenue ($)"),
                              yaxis2=dict(title="ROAS (%)", overlaying="y", side="right"),
                              legend=dict(orientation="h"), height=340)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("⚠️ Revenue has a 30-day attribution window. Recent months may undercount — P2 revenue will grow as more conversions are attributed.")
        with t3:
            fig = px.bar(mo, x="Month", y="Conv_pct",
                         labels={"Conv_pct":"Install → Customer %"},
                         color_discrete_sequence=["#B279A2"])
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)

    # ── Year campaign snapshot ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("12-Month Campaign Snapshot (Active & Key Campaigns)")

    if not yr_camps.empty:
        jm = yr_camps[yr_camps["App Name"] == "Judge.me Product Reviews App"].copy()
        jm = jm[jm["Installs"] > 0].sort_values("Installs", ascending=False)
        jm["ROAS_pct"] = jm["Return On Spend"] * 100
        jm["CPI"]      = jm["Cost Per Install"]

        disp = jm[["Campaign","Status","Daily Budget","Installs","Spend","CPI","Customers","Revenue","ROAS_pct"]].copy()
        disp["Spend"]       = disp["Spend"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
        disp["CPI"]         = disp["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        disp["Revenue"]     = disp["Revenue"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
        disp["ROAS_pct"]    = disp["ROAS_pct"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "—")
        disp["Daily Budget"]= disp["Daily Budget"].apply(lambda x: f"${x:.0f}" if pd.notna(x) else "—")
        disp["Customers"]   = disp["Customers"].apply(lambda x: f"{int(x)}" if pd.notna(x) else "—")
        st.dataframe(disp.rename(columns={"ROAS_pct":"ROAS","Daily Budget":"Budget/Day"}),
                     use_container_width=True)


def page_trends(daily, p2_camps):
    st.title("📅 Trends & Timeline")
    st.caption("Daily install trend Aug 21, 2025 – Apr 15, 2026. Red lines = change dates (Feb 24, Mar 18). Note: last week is partial (Apr 13–15 only).")

    if daily.empty:
        st.error("Daily data not available.")
        return

    col1, col2 = st.columns([2,1])
    camp_opts = ["All"] + sorted(daily["Campaign"].dropna().unique().tolist())
    camp_sel  = col1.selectbox("Campaign:", camp_opts, key="trend_camp")
    metric    = col2.selectbox("Metric:", ["Installs","Spend","CPI","Customers"], key="trend_metric")

    df = daily.copy() if camp_sel == "All" else daily[daily["Campaign"] == camp_sel].copy()
    agg = df.groupby("Date").agg(
        Installs=("Installs","sum"), Spend=("Spend","sum"), Customers=("Customers","sum"),
    ).reset_index().sort_values("Date")
    agg["CPI"]   = agg["Spend"] / agg["Installs"].replace(0, None)
    agg["Roll7"] = agg[metric if metric != "CPI" else "Installs"].rolling(7, min_periods=3).mean()

    p2_avg = None
    if not p2_camps.empty:
        if metric == "Installs":    p2_avg = p2_camps["Installs"].sum() / 22
        elif metric == "Spend":     p2_avg = p2_camps["Spend"].sum() / 22
        elif metric == "Customers": p2_avg = p2_camps["Customers"].sum() / 22

    # ── Main chart ────────────────────────────────────────────────────────────
    fig = go.Figure()
    y_raw = agg[metric] if metric != "CPI" else agg["CPI"]
    roll  = agg["Roll7"] if metric != "CPI" else agg["CPI"].rolling(7, min_periods=3).mean()

    fig.add_scatter(x=agg["Date"], y=y_raw, name=f"Daily {metric}",
                    mode="lines", line=dict(color="#c0c8d8", width=1), opacity=0.5)
    fig.add_scatter(x=agg["Date"], y=roll,  name="7-Day Avg",
                    mode="lines", line=dict(color="#4C78A8", width=2.5))

    if p2_avg is not None:
        fig.add_shape(type="line", x0="2026-02-24", x1="2026-03-17",
                      y0=p2_avg, y1=p2_avg,
                      line=dict(color="#82b366", width=2, dash="dot"))
        fig.add_annotation(x="2026-03-10", y=p2_avg * 1.04,
                           text=f"P2 avg: {p2_avg:.0f}", showarrow=False,
                           font=dict(color="#82b366", size=11))

    fig.add_vline(x="2026-02-24", line_width=2, line_dash="dash", line_color="#E45756")
    fig.add_annotation(x="2026-02-24", y=1, yref="paper", text="⚡ Keyword/Bid Changes",
                       showarrow=False, xanchor="left", font=dict(color="#E45756", size=11))
    fig.update_layout(height=420, yaxis_title=metric, hovermode="x unified",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Stacked weekly by campaign ────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Weekly Installs by Campaign")
    daily["Week"] = daily["Date"].dt.to_period("W").dt.start_time
    wk = daily.groupby(["Week","Campaign"])["Installs"].sum().reset_index()
    fig2 = px.area(wk.sort_values("Week"), x="Week", y="Installs", color="Campaign",
                   color_discrete_map=CAMPAIGN_COLORS,
                   title="Weekly installs stacked by campaign — change happens at the red line")
    fig2.add_vline(x="2026-02-24", line_width=2, line_dash="dash", line_color="#E45756")
    fig2.update_layout(height=360, hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig2, use_container_width=True)

    # ── ROAS / CPI trend ─────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("ROAS & CPI — Monthly Trend")
    daily["Month"] = daily["Date"].dt.to_period("M").astype(str)
    mo = daily.groupby("Month").agg(
        Installs=("Installs","sum"), Spend=("Spend","sum"),
        Revenue=("Revenue","sum"),
    ).reset_index()
    mo["CPI"]  = mo["Spend"] / mo["Installs"]
    mo["ROAS"] = mo["Revenue"] / mo["Spend"] * 100

    if not p2_camps.empty:
        p2_rev = p2_camps["Revenue"].sum(); p2_spd = p2_camps["Spend"].sum()
        mo = pd.concat([mo, pd.DataFrame([{
            "Month":"2026-P2","Installs":p2_camps["Installs"].sum(),
            "Spend":p2_spd,"Revenue":p2_rev,
            "CPI":p2_spd/p2_camps["Installs"].sum() if p2_camps["Installs"].sum()>0 else 0,
            "ROAS":p2_rev/p2_spd*100 if p2_spd>0 else 0,
        }])], ignore_index=True)

    fig3 = go.Figure()
    fig3.add_scatter(x=mo["Month"], y=mo["ROAS"], name="ROAS (%)",
                     mode="lines+markers", line=dict(color="#E45756", width=2.5), marker=dict(size=8))
    fig3.add_scatter(x=mo["Month"], y=mo["CPI"],  name="CPI ($)", yaxis="y2",
                     mode="lines+markers", line=dict(color="#4C78A8", width=2), marker=dict(size=6))
    fig3.update_layout(
        yaxis=dict(title="ROAS (%)"),
        yaxis2=dict(title="CPI ($)", overlaying="y", side="right"),
        height=360, legend=dict(orientation="h"),
        title="ROAS is falling while CPI improves — cheaper traffic, fewer paying customers",
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("⚠️ Attribution note: revenue is attributed over a 30-day window. P2 and the most recent months will show lower ROAS until conversions catch up — but the downward trend predates P2.")


def page_campaigns(daily, yr_camps, p2_camps):
    st.title("🎯 Campaign Breakdown")

    # ── Full-year table ───────────────────────────────────────────────────────
    st.subheader("12-Month Overview — All Campaigns (Apr 2025 – Apr 2026)")
    st.caption("Only Judge.me Product Reviews App. Sorted by installs.")

    if not yr_camps.empty:
        jm = yr_camps[yr_camps["App Name"] == "Judge.me Product Reviews App"].copy()
        jm["ROAS_pct"] = jm["Return On Spend"] * 100
        jm["CPI"]      = jm["Cost Per Install"]
        jm["Rev/Customer"] = jm.apply(
            lambda r: r["Revenue"]/r["Customers"] if pd.notna(r["Customers"]) and r["Customers"]>0 else None, axis=1)
        jm_sorted = jm.sort_values("Installs", ascending=False)

        # Colour-coded bar chart: ROAS
        active = jm[jm["Installs"] > 0]
        fig = px.bar(active.sort_values("ROAS_pct", ascending=False),
                     x="Campaign", y="ROAS_pct",
                     color="ROAS_pct", color_continuous_scale="RdYlGn",
                     labels={"ROAS_pct":"ROAS (%)"},
                     title="12-Month ROAS by Campaign — BrandProtection is the clear winner",
                     text="ROAS_pct")
        fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig.update_layout(height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        # Spend vs Revenue scatter
        fig2 = px.scatter(active, x="Spend", y="Revenue", size="Installs",
                          color="Campaign", color_discrete_map=CAMPAIGN_COLORS,
                          hover_name="Campaign", text="Campaign",
                          labels={"Spend":"12M Spend ($)","Revenue":"12M Revenue ($)"},
                          title="Spend vs Revenue — campaigns above the diagonal are profitable")
        # Add break-even line
        max_val = max(active["Spend"].max(), active["Revenue"].max()) * 1.1
        fig2.add_scatter(x=[0, max_val], y=[0, max_val],
                         mode="lines", line=dict(color="grey", dash="dash", width=1),
                         name="Break-even", showlegend=True)
        fig2.update_traces(textposition="top center")
        fig2.update_layout(height=460, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Full table
        st.subheader("Detail Table")
        d = jm_sorted[["Campaign","Status","Daily Budget","Installs","Spend","CPI",
                        "Customers","Revenue","ROAS_pct","Rev/Customer"]].copy()
        d["Spend"]        = d["Spend"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
        d["CPI"]          = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        d["Revenue"]      = d["Revenue"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
        d["ROAS_pct"]     = d["ROAS_pct"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "—")
        d["Rev/Customer"] = d["Rev/Customer"].apply(lambda x: f"${x:.0f}" if pd.notna(x) else "—")
        d["Daily Budget"] = d["Daily Budget"].apply(lambda x: f"${x:.0f}" if pd.notna(x) else "—")
        d["Customers"]    = d["Customers"].apply(lambda x: f"{int(x)}" if pd.notna(x) else "—")
        st.dataframe(d.rename(columns={"ROAS_pct":"ROAS","Daily Budget":"Budget/Day","Rev/Customer":"Rev/Cust"}),
                     use_container_width=True)

    st.markdown("---")

    # ── P1 vs P2 comparison ───────────────────────────────────────────────────
    st.subheader("P1 vs P2 Campaign Installs/Day")
    if not daily.empty and not p2_camps.empty:
        p1_camp = daily.groupby("Campaign").agg(
            P1_Installs=("Installs","sum"), P1_Spend=("Spend","sum"),
        ).reset_index()
        p1_camp["P1_IPD"] = p1_camp["P1_Installs"] / 181
        p1_camp["P1_CPI"] = p1_camp["P1_Spend"] / p1_camp["P1_Installs"].replace(0, None)

        p2_c = p2_camps[["Campaign","Installs","Spend"]].rename(
            columns={"Installs":"P2_Installs","Spend":"P2_Spend"})
        p2_c["P2_IPD"] = p2_c["P2_Installs"] / 22

        comp = pd.merge(p1_camp, p2_c, on="Campaign", how="outer").fillna(0)
        rows = []
        for _, r in comp.iterrows():
            if r["P1_IPD"] > 0:
                rows.append({"Campaign":r["Campaign"],"Period":P1_LABEL,"Installs/Day":r["P1_IPD"]})
            if r["P2_IPD"] > 0:
                rows.append({"Campaign":r["Campaign"],"Period":P2_LABEL,"Installs/Day":r["P2_IPD"]})
        if rows:
            fig3 = px.bar(pd.DataFrame(rows), x="Campaign", y="Installs/Day", color="Period",
                          barmode="group",
                          color_discrete_map={P1_LABEL:"#6c8ebf", P2_LABEL:"#82b366"})
            fig3.update_layout(height=360)
            st.plotly_chart(fig3, use_container_width=True)


def page_keywords(p1_kw, p2_kw, comp):
    st.title("🔑 Keyword Performance")
    st.caption("P1: Aug 21–Feb 18 (181 days) vs P2: Feb 24–Mar 17 (22 days)")

    if comp.empty:
        st.error("No keyword comparison data.")
        return

    # Filters
    c1, c2, c3 = st.columns(3)
    status_opts = sorted(comp["Status"].unique())
    camp_opts   = sorted(comp["Campaign"].dropna().unique())
    status_sel  = c1.multiselect("Status:", status_opts, default=status_opts)
    camp_sel    = c2.multiselect("Campaign:", camp_opts, default=camp_opts)
    min_inst    = c3.number_input("Min P2 installs:", 0, value=0, step=1)

    view = comp[
        comp["Status"].isin(status_sel) &
        comp["Campaign"].isin(camp_sel) &
        (comp["P2_Installs"] >= min_inst)
    ].copy().sort_values("P2_IPD", ascending=False)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Keywords", len(view))
    c2.metric("New in P2", len(view[view["Status"]=="New in P2"]))
    c3.metric("Bid Increased", len(view[view["Status"]=="Bid Increased"]))
    c4.metric("Dropped in P2", len(view[view["Status"]=="Dropped in P2"]))

    # Table
    cols = {"Keyword":"Keyword","Match":"Match","Campaign":"Campaign","Status":"Status",
            "P1_IPD":"P1 Inst/Day","P2_IPD":"P2 Inst/Day","Delta_IPD_Pct":"Δ%",
            "P1_CPI":"P1 CPI","P2_CPI":"P2 CPI","P1_Bid":"P1 Bid","P2_Bid":"P2 Bid",
            "P2_Installs":"P2 Installs","P2_Spend":"P2 Spend"}
    disp = view[[c for c in cols if c in view.columns]].rename(columns=cols)
    for col in ["P1 Inst/Day","P2 Inst/Day"]:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    for col in ["P1 CPI","P2 CPI","P1 Bid","P2 Bid"]:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    if "Δ%" in disp.columns:
        disp["Δ%"] = disp["Δ%"].apply(
            lambda x: f"+{x:.0f}%" if (pd.notna(x) and x>0) else (f"{x:.0f}%" if pd.notna(x) else "NEW"))
    if "P2 Spend" in disp.columns:
        disp["P2 Spend"] = disp["P2 Spend"].apply(lambda x: f"${x:.0f}" if pd.notna(x) else "—")
    st.dataframe(disp, use_container_width=True)

    # Top keywords chart
    st.markdown("---")
    st.subheader("Top 20 by P2 Installs/Day")
    top = view.nlargest(20, "P2_IPD")
    if not top.empty:
        fig = px.bar(top.sort_values("P2_IPD"), x="P2_IPD", y="Keyword",
                     orientation="h", color="Campaign", color_discrete_map=CAMPAIGN_COLORS,
                     labels={"P2_IPD":"P2 Installs/Day"})
        fig.update_layout(height=520, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # Bid increase impact
    bid_df = view[view["Status"]=="Bid Increased"].copy()
    if not bid_df.empty:
        st.markdown("---")
        st.subheader("Bid Increase Impact — Did Higher Bids Actually Help?")
        imp = bid_df[bid_df["Delta_IPD"]>0]; dec = bid_df[bid_df["Delta_IPD"]<0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Keywords with bid increase", len(bid_df))
        c2.metric("Volume improved ✅", len(imp))
        c3.metric("Volume declined ❌", len(dec))
        rows = []
        for _, r in bid_df.iterrows():
            rows.append({"Keyword":r["Keyword"],"Period":P1_LABEL,"Installs/Day":r["P1_IPD"]})
            rows.append({"Keyword":r["Keyword"],"Period":P2_LABEL,"Installs/Day":r["P2_IPD"]})
        fig2 = px.bar(pd.DataFrame(rows), x="Installs/Day", y="Keyword", color="Period",
                      barmode="group", orientation="h",
                      color_discrete_map={P1_LABEL:"#6c8ebf",P2_LABEL:"#82b366"}, height=460)
        st.plotly_chart(fig2, use_container_width=True)


def page_splits(country_df, device_df, plan_df):
    st.title("🌍 Audience Splits")
    st.caption("Source: 90-day search term detail (Jan 8 – Apr 7, 2026) — 130k rows, Judge.me Product Reviews App only.")

    tab1, tab2, tab3 = st.tabs(["🌏 Country","📱 Device","💳 Shop Plan"])

    with tab1:
        if country_df.empty:
            st.info("No data.")
            return
        agg = country_df.groupby("Country Code").agg(
            Installs=("Installs","sum"), Spend=("Spend","sum"),
            Customers=("Customers","sum"), Revenue=("Revenue","sum"),
        ).reset_index()
        agg["CPI"]       = agg["Spend"] / agg["Installs"].replace(0, None)
        agg["Conv_pct"]  = agg["Customers"] / agg["Installs"].replace(0, None) * 100
        agg["ROAS_pct"]  = agg["Revenue"] / agg["Spend"].replace(0, None) * 100
        agg["Install_pct"]= agg["Installs"] / agg["Installs"].sum() * 100
        agg = agg.sort_values("Installs", ascending=False)
        top = agg.head(25)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(top.sort_values("Installs"), x="Installs", y="Country Code",
                         orientation="h", title="Top 25 Countries by Installs",
                         color="CPI", color_continuous_scale="RdYlGn_r",
                         labels={"CPI":"CPI ($)"})
            fig.update_layout(height=560)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            conv_data = top[top["Customers"]>0]
            fig2 = px.scatter(conv_data, x="CPI", y="Conv_pct",
                              size="Installs", color="Country Code",
                              hover_name="Country Code",
                              title="CPI vs Conversion Rate (bubble = installs)",
                              labels={"Conv_pct":"Install→Customer %","CPI":"CPI ($)"})
            fig2.update_layout(height=560, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Table
        d = top.copy()
        d["CPI"]        = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        d["Conv_pct"]   = d["Conv_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        d["ROAS_pct"]   = d["ROAS_pct"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "—")
        d["Install_pct"]= d["Install_pct"].apply(lambda x: f"{x:.1f}%")
        d["Spend"]      = d["Spend"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(d.rename(columns={"Install_pct":"% of Installs","Conv_pct":"Conv%","ROAS_pct":"ROAS"}),
                     use_container_width=True)

        total = agg["Installs"].sum()
        in_pk = agg[agg["Country Code"].isin(["IN","PK"])]["Installs"].sum()
        in_pk_cust = agg[agg["Country Code"].isin(["IN","PK"])]["Customers"].sum()
        st.info(
            f"📌 **India + Pakistan = {in_pk/total*100:.0f}% of installs** "
            f"with only {int(in_pk_cust)} attributed customers. "
            f"These markets drive volume at low CPI but convert to paying customers at much lower rates than US/UK/AU."
        )

    with tab2:
        if device_df.empty:
            st.info("No data.")
            return
        agg = device_df.groupby("Device Type").agg(
            Installs=("Installs","sum"), Spend=("Spend","sum"),
            Customers=("Customers","sum"), Revenue=("Revenue","sum"),
        ).reset_index()
        agg["CPI"]      = agg["Spend"] / agg["Installs"].replace(0, None)
        agg["Conv_pct"] = agg["Customers"] / agg["Installs"].replace(0, None) * 100
        agg["ROAS_pct"] = agg["Revenue"] / agg["Spend"].replace(0, None) * 100

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(agg, values="Installs", names="Device Type",
                         title="Installs by Device", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(agg, x="Device Type", y=["Installs","Customers"], barmode="group",
                          title="Installs vs Customers by Device",
                          color_discrete_map={"Installs":"#4C78A8","Customers":"#54A24B"})
            st.plotly_chart(fig2, use_container_width=True)

        d = agg.copy()
        d["CPI"]     = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        d["Conv_pct"]= d["Conv_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        d["ROAS_pct"]= d["ROAS_pct"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "—")
        d["Spend"]   = d["Spend"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(d.rename(columns={"Conv_pct":"Conv%","ROAS_pct":"ROAS"}), use_container_width=True)

    with tab3:
        if plan_df.empty:
            st.info("No data.")
            return
        agg = plan_df.groupby("Shop Plan").agg(
            Installs=("Installs","sum"), Spend=("Spend","sum"),
            Customers=("Customers","sum"), Revenue=("Revenue","sum"),
        ).reset_index()
        agg["CPI"]          = agg["Spend"] / agg["Installs"].replace(0, None)
        agg["Conv_pct"]     = agg["Customers"] / agg["Installs"].replace(0, None) * 100
        agg["Rev_per_Inst"] = agg["Revenue"] / agg["Installs"].replace(0, None)
        agg = agg.sort_values("Installs", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(agg, values="Installs", names="Shop Plan", title="Installs by Plan", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(agg, x="Shop Plan", y="Conv_pct", color="Shop Plan",
                          title="Conversion Rate by Plan (%)",
                          labels={"Conv_pct":"Install→Customer %"})
            st.plotly_chart(fig2, use_container_width=True)

        d = agg.copy()
        d["CPI"]          = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        d["Conv_pct"]     = d["Conv_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        d["Rev_per_Inst"] = d["Rev_per_Inst"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        d["Spend"]        = d["Spend"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(d.rename(columns={"Conv_pct":"Conv%","Rev_per_Inst":"Rev/Install"}),
                     use_container_width=True)


def page_search_terms(search_df, p2_kw):
    st.title("🔍 Search Term Explorer")
    st.caption("Source: 90-day data (Jan 8 – Apr 7, 2026). Aggregated by search term across all country/device/plan splits.")

    if search_df.empty:
        st.error("Search term data not available.")
        return

    c1, c2 = st.columns([2,1])
    camp_sel  = c1.selectbox("Campaign:", ["All"] + sorted(search_df["Campaign"].dropna().unique()))
    min_inst  = c2.number_input("Min installs:", 0, value=1, step=1)

    df = search_df.copy()
    if camp_sel != "All":
        df = df[df["Campaign"] == camp_sel]
    df = df[df["Installs"] >= min_inst].copy()
    df["CPI"]         = df["Spend"] / df["Installs"].replace(0, None)
    df["InstallRate"] = df["Installs"] / df["Clicks"].replace(0, None)
    df = df.sort_values("Installs", ascending=False)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique search terms",  df["Search Term"].nunique())
    c2.metric("Total installs",       f"{int(df['Installs'].sum()):,}")
    c3.metric("Total spend",          f"${df['Spend'].sum():,.0f}")
    c4.metric("Avg CPI",              f"${df['Spend'].sum()/df['Installs'].sum():.2f}" if df["Installs"].sum()>0 else "—")

    disp = df[["Campaign","Search Term","Keyword","Match Type","Impressions","Installs","Spend","CPI","InstallRate"]].head(200).copy()
    disp["CPI"]         = disp["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    disp["InstallRate"] = disp["InstallRate"].apply(lambda x: f"{x*100:.0f}%" if pd.notna(x) else "—")
    disp["Spend"]       = disp["Spend"].apply(lambda x: f"${x:.0f}")
    st.dataframe(disp, use_container_width=True)

    # Opportunities
    st.markdown("---")
    st.subheader("🆕 Keyword Opportunities — High Installs, Not Yet Exact Match")
    st.caption("Search terms with ≥5 installs that aren't exact-match keywords in P2")

    if not p2_kw.empty:
        p2_exact = set(p2_kw[p2_kw["Match"]=="exact"]["Keyword"].str.lower())
        opp = search_df[
            (~search_df["Search Term"].str.lower().isin(p2_exact)) &
            (search_df["Installs"] >= 5)
        ].copy()
        opp["CPI"] = opp["Spend"] / opp["Installs"].replace(0, None)
        opp = opp.sort_values("Installs", ascending=False).head(40)
        if not opp.empty:
            d = opp[["Campaign","Search Term","Keyword","Match Type","Installs","Spend","CPI"]].copy()
            d["CPI"]   = d["CPI"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
            d["Spend"] = d["Spend"].apply(lambda x: f"${x:.0f}")
            st.dataframe(d, use_container_width=True)
        else:
            st.success("All high-volume search terms are already exact-match keywords.")


def page_diagnosis(daily, yr_camps, p2_camps, p1_kw, p2_kw, country_df):
    st.title("💡 Diagnosis & Recommendations")
    st.caption("Goal: maximize install volume. Only cut keywords with proven zero installs — keep everything that drives volume.")

    # ── Install trend ─────────────────────────────────────────────────────────
    st.subheader("🔎 What Happened to Installs")

    if not daily.empty:
        dc = daily.copy()
        dc["Week"] = dc["Date"].dt.to_period("W").dt.start_time
        wk = dc.groupby("Week").agg(Installs=("Installs","sum")).reset_index().sort_values("Week")
        if len(wk) > 1 and wk.iloc[-1]["Installs"] < wk.iloc[-2]["Installs"] * 0.5:
            wk = wk.iloc[:-1]
        peak_wk   = wk.loc[wk["Installs"].idxmax()]
        latest_wk = wk.iloc[-1]
        pct_drop  = (latest_wk["Installs"] / peak_wk["Installs"] - 1) * 100

        c1, c2, c3, c4 = st.columns(4)
        p1_ipd = daily["Installs"].sum() / 181
        c1.metric("P1 Avg Installs/Day", f"{p1_ipd:.0f}")
        if not p2_camps.empty:
            p2_ipd = p2_camps["Installs"].sum() / 22
            c2.metric("P2 Avg Installs/Day", f"{p2_ipd:.0f}", delta=f"{p2_ipd-p1_ipd:+.0f}")
        c3.metric("Peak Weekly Installs", f"{int(peak_wk['Installs'])} (Feb 23)")
        c4.metric("Latest Full Week",     f"{int(latest_wk['Installs'])} ({pct_drop:+.0f}% vs peak)")

    st.markdown("---")
    st.subheader("🔬 Why Installs Are Declining")
    st.markdown("""
**1. Install volume peaked Feb 23 then declined every week after the changes**
The Feb 24 bid raises and keyword additions didn't grow volume — installs fell steadily from
786/week at peak to ~600/week by early April (-24%). The changes weren't the cause of the decline
(it started earlier) but they also didn't reverse it.

**2. BrandProtection and PLUS-ProductReview are massively underinvested**
These two campaigns have the best performance in the account but are capped at $20/day and $10/day respectively.
Raising their budgets is the single fastest way to get more installs with proven conversion.
- **BrandProtection:** $0.28 CPI, 145 paying customers from $849 spend over 12 months
- **PLUS-ProductReview:** targets Shopify Plus merchants, 313% ROAS, currently paused

**3. Dormant competitor keywords are wasting bid headroom**
Many Competitors campaign keywords were added at $1.00 bid — they get zero impressions because
$1 cannot win any Shopify App Store auction. These slots should either be raised to $2.50+ or cut,
so that budget flows to keywords that are actually competing.

**4. `review` and `shopify product reviews` can scale further**
These are the top two install-volume keywords in the account (1,836 and 385 installs in the last period).
Both responded well to bid increases. There is likely more headroom to push volume higher.

**5. Revenue attribution lag makes ROAS look worse than it is**
The 30-day attribution window means recent installs won't show revenue for another 2–4 weeks.
Focus on install volume as the leading indicator, not ROAS, until attribution catches up.
""")

    st.markdown("---")
    st.subheader("🔴 Pause These — Zero Installs, Pure Dead Weight")
    st.caption("These keywords have spent budget across multiple periods and produced zero or near-zero installs. Pausing frees ~$8/day to add to top performers.")
    pause = [
        {"Keyword":"q&a (broad)","Campaign":"Features","3M Installs":1,"3M Spend":"~$30","Reason":"1 install from $30 spend. Not a Shopify app search intent."},
        {"Keyword":"rich snippet (broad)","Campaign":"Features","3M Installs":1,"3M Spend":"~$20","Reason":"1 install from $20 spend. SEO concept, not app intent."},
        {"Keyword":"question (broad)","Campaign":"Trust","3M Installs":2,"3M Spend":"~$70","Reason":"2 installs from $70 across 2 campaigns."},
        {"Keyword":"loox - photo reviews (exact)","Campaign":"Competitors","3M Installs":0,"3M Spend":"~$10","Reason":"0 installs confirmed across P1, P2, P3."},
        {"Keyword":"rivo reviews (exact)","Campaign":"Competitors","3M Installs":0,"3M Spend":"~$10","Reason":"0 installs confirmed across P1, P2, P3."},
        {"Keyword":"All $1.00-bid Competitor keywords","Campaign":"Competitors","3M Installs":0,"3M Spend":"—","Reason":"$1 bid cannot win any auction on Shopify App Store. Zero impressions."},
    ]
    st.dataframe(pd.DataFrame(pause), use_container_width=True)
    st.warning("Note: `google reviews` (171 installs) and `google review` (102 installs) are NOT on this list — they drive real volume and should stay.")

    st.markdown("---")
    st.subheader("🟢 Scale These for More Installs")
    scale = [
        {"Priority":"#1","Action":"Budget $20→$150/day","Campaign":"BrandProtection","Evidence":"$0.28 CPI, 145 customers from $849 spend (12 months). Most efficient campaign in the account. Budget is the only constraint."},
        {"Priority":"#2","Action":"Reactivate + budget $10→$75/day","Campaign":"PLUS-ProductReview","Evidence":"313% ROAS, targets Shopify Plus merchants. Currently paused. 33 customers from $967 spend."},
        {"Priority":"#3","Action":"Increase bid $2.50→$3.50","Keyword":"review (exact)","Campaign":"ProductReview","Evidence":"1,836 installs in last period — top volume keyword in account. Likely hitting budget cap. More bid = more impressions."},
        {"Priority":"#4","Action":"Increase bid $3.50→$4.50","Keyword":"shopify product reviews (exact)","Campaign":"ProductReview","Evidence":"385 installs last period, +195% after last raise. Still scaling well."},
        {"Priority":"#5","Action":"Increase bid $5.00→$6.50","Keyword":"review widget (broad)","Campaign":"ProductReview","Evidence":"282 installs last period. Broad match with strong install rate — bid up to capture more volume."},
        {"Priority":"#6","Action":"Increase bid $7.00→$9.00","Keyword":"stars (broad)","Campaign":"Trust","Evidence":"81 installs last period. 84% install rate. More headroom available at higher bid."},
        {"Priority":"#7","Action":"Raise bid $1.00→$2.50+ or pause","Keyword":"All dormant Competitor keywords","Campaign":"Competitors","Evidence":"$1 bid = 0 impressions. Either compete properly or free that budget for active keywords."},
    ]
    st.dataframe(pd.DataFrame(scale), use_container_width=True)

    st.markdown("---")
    st.subheader("🆕 New Keywords to Add for More Volume")
    st.markdown("These are high-intent searches that can bring incremental installs. Add as exact match first, then test broad.")
    new_kws = [
        {"Keyword":"shopify reviews app","Match":"exact","Suggested Bid":"$2.50","Campaign":"ProductReview","Rationale":"Direct competitor to top existing keywords, high commercial intent"},
        {"Keyword":"product review app","Match":"exact","Suggested Bid":"$2.50","Campaign":"ProductReview","Rationale":"Generic reviews app intent — broad install potential"},
        {"Keyword":"review app shopify","Match":"exact","Suggested Bid":"$2.00","Campaign":"ProductReview","Rationale":"Same intent as top performer, different word order"},
        {"Keyword":"photo reviews","Match":"exact","Suggested Bid":"$2.00","Campaign":"ProductReview","Rationale":"Visual review intent — Judge.me supports this, competitor to Loox"},
        {"Keyword":"star rating app","Match":"exact","Suggested Bid":"$2.00","Campaign":"Trust","Rationale":"Trust/rating intent, complements existing 'stars' broad keyword"},
        {"Keyword":"review request app","Match":"exact","Suggested Bid":"$2.00","Campaign":"ProductReview","Rationale":"Post-purchase review automation intent — Judge.me core feature"},
        {"Keyword":"stamped reviews","Match":"exact","Suggested Bid":"$2.50","Campaign":"Competitors","Rationale":"Direct Stamped.io competitor — same audience as Loox/Yotpo targeting"},
        {"Keyword":"ali reviews","Match":"exact","Suggested Bid":"$2.00","Campaign":"Competitors","Rationale":"Popular reviews importer app, merchants switching often search this"},
        {"Keyword":"review management app","Match":"broad","Suggested Bid":"$2.00","Campaign":"Features","Rationale":"Broader intent, captures merchants searching for review tools"},
        {"Keyword":"shopify trust badges","Match":"broad","Suggested Bid":"$1.50","Campaign":"Trust","Rationale":"Trust-building intent adjacent to reviews — complements Trust campaign"},
    ]
    st.dataframe(pd.DataFrame(new_kws), use_container_width=True)

    st.markdown("---")
    st.subheader("💰 Where to Add Budget")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Free up ~$8/day from true dead-weight keywords:**")
        st.markdown("- `q&a` + `rich snippet` + `question` ≈ $4/day\n- `loox photo` + `rivo reviews` ≈ $2/day\n- Dead $1-bid competitor slots ≈ $2/day")
    with col2:
        st.markdown("**Add budget where volume is proven:**")
        st.markdown("""
- BrandProtection: add $130/day (highest priority — $0.28 CPI)
- PLUS-ProductReview: reactivate at $75/day
- ProductReview campaign: raise daily cap to feed `review` and `review widget` keywords
""")
    st.info(
        "The goal is more installs, not cost savings. "
        "Free up dead-weight spend and immediately move it into campaigns/keywords with proven install volume. "
        "BrandProtection alone at $150/day could add 350+ installs/day based on current CPI."
    )

    st.markdown("---")
    st.subheader("✅ Action Checklist")
    actions = [
        ("🔴 PAUSE", "q&a + rich snippet + question (broad)",         "Near-zero installs across all periods"),
        ("🔴 PAUSE", "loox - photo reviews + rivo reviews (exact)",   "0 installs confirmed across 3 snapshots"),
        ("🔴 RAISE OR PAUSE", "All $1.00-bid Competitor keywords",    "Can't win auctions at $1 — zero impressions"),
        ("🟢 SCALE", "BrandProtection budget $20→$150/day",           "$0.28 CPI — #1 highest-priority action"),
        ("🟢 REACTIVATE", "PLUS-ProductReview $10→$75/day",           "313% ROAS, targets Plus merchants"),
        ("🟢 INCREASE BID", "review (exact) $2.50→$3.50",             "Top volume keyword, 1,836 installs/period"),
        ("🟢 INCREASE BID", "shopify product reviews $3.50→$4.50",    "+195% after last raise, still scaling"),
        ("🟢 INCREASE BID", "review widget (broad) $5.00→$6.50",      "282 installs last period"),
        ("🟢 INCREASE BID", "stars (broad) $7.00→$9.00",              "81 installs, 84% install rate"),
        ("🆕 ADD KEYWORD",  "shopify reviews app (exact) @ $2.50",    "High-intent, no overlap with existing"),
        ("🆕 ADD KEYWORD",  "product review app (exact) @ $2.50",     "Broad install intent"),
        ("🆕 ADD KEYWORD",  "stamped reviews (exact) @ $2.50",        "Competitor gap — not currently targeted"),
        ("🆕 ADD KEYWORD",  "review request app (exact) @ $2.00",     "Judge.me core feature, high intent"),
        ("🟡 INVESTIGATE",  "Product funnel changes Nov–Dec 2025",     "ROAS decline predates ad changes — may be a funnel issue"),
    ]
    for action, kw, note in actions:
        st.checkbox(f"**{action}** `{kw}` — {note}", key=f"chk_{kw[:40]}")


def page_changelog(changelog, daily):
    st.title("📋 Change Log")
    st.caption(
        "All keyword and bid changes across Feb 24 and Mar 18–Apr 15, 2026. "
        "159 events reconstructed from 3 keyword snapshots (Feb 18, Mar 17, Apr 15)."
    )

    if changelog.empty:
        st.error("Change log data not available.")
        return

    # ── Summary metrics ───────────────────────────────────────────────────────
    n_bid  = len(changelog[changelog["Change Type"] == "Bid Change"])
    n_add  = len(changelog[changelog["Change Type"] == "Keyword Added"])
    n_drop = len(changelog[changelog["Change Type"] == "Keyword Dropped"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Events",     len(changelog))
    c2.metric("Bid Changes",      n_bid)
    c3.metric("Keywords Added",   n_add)
    c4.metric("Keywords Dropped", n_drop)

    # ── Weekly install trend with change events annotated ─────────────────────
    st.markdown("---")
    st.subheader("Weekly Install Trend — Change Events Annotated")

    if not daily.empty:
        dc = daily.copy()
        dc["Week"] = dc["Date"].dt.to_period("W").dt.start_time
        wk = dc.groupby("Week").agg(Installs=("Installs","sum")).reset_index().sort_values("Week")

        # Drop last partial week if it looks truncated
        if len(wk) > 1:
            prev_avg = wk.iloc[-8:-1]["Installs"].mean() if len(wk) >= 8 else wk.iloc[:-1]["Installs"].mean()
            if wk.iloc[-1]["Installs"] < prev_avg * 0.5:
                wk = wk.iloc[:-1]

        fig = go.Figure()
        fig.add_scatter(
            x=wk["Week"], y=wk["Installs"],
            mode="lines+markers", name="Weekly Installs",
            line=dict(color="#4C78A8", width=2.5), marker=dict(size=7),
        )
        fig.add_vline(x="2026-02-23", line_width=2, line_dash="dash", line_color="#E45756")
        fig.add_annotation(x="2026-02-23", y=1, yref="paper", text="Feb 24: bid raises + new keywords",
                           showarrow=False, xanchor="left", font=dict(color="#E45756", size=11))
        fig.add_vline(x="2026-03-16", line_width=2, line_dash="dash", line_color="#F58518")
        fig.add_annotation(x="2026-03-16", y=0.92, yref="paper", text="Mar 18+: bid changes + dropped kws",
                           showarrow=False, xanchor="right", font=dict(color="#F58518", size=11))
        fig.update_layout(height=400, yaxis_title="Weekly Installs", hovermode="x unified",
                          title="Installs peaked at 786/week (Feb 23). Trended down every week after changes.")
        st.plotly_chart(fig, use_container_width=True)

        wk_recent = wk[wk["Week"] >= pd.Timestamp("2026-02-16")].copy()
        if len(wk_recent) >= 2:
            peak = wk_recent["Installs"].max()
            wk_recent["vs Peak"] = ((wk_recent["Installs"] / peak - 1) * 100).round(1).astype(str) + "%"
            wk_recent["Week"] = wk_recent["Week"].dt.strftime("%b %d")
            st.dataframe(wk_recent[["Week","Installs","vs Peak"]].rename(columns={"vs Peak":"vs Feb 23 Peak"}),
                         use_container_width=False, hide_index=True)

    # ── Per-period tabs ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Changes by Period")

    feb24 = changelog[changelog["Date"] == "~Feb 24, 2026"].copy()
    mar18 = changelog[changelog["Date"] == "Mar 18 – Apr 15, 2026"].copy()

    tab1, tab2 = st.tabs([
        f"Feb 24 Changes ({len(feb24)} events)",
        f"Mar 18–Apr 15 Changes ({len(mar18)} events)",
    ])

    with tab1:
        bid1 = feb24[feb24["Change Type"] == "Bid Change"]
        add1 = feb24[feb24["Change Type"] == "Keyword Added"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{len(bid1)} Bid Changes**")
            if not bid1.empty:
                st.dataframe(bid1[["Campaign","Keyword","Match Type","From","To","Direction","P2 Installs"]],
                             use_container_width=True, hide_index=True)
                raised = bid1[bid1["Direction"] == "▲ Raised"]
                good = raised[raised["P2 Installs"] >= 20]
                bad  = raised[raised["P2 Installs"] < 5]
                st.info(f"Of {len(raised)} raises: **{len(good)} drove ≥20 installs** in P2, **{len(bad)} got <5 installs** despite higher bid.")
        with c2:
            st.markdown(f"**{len(add1)} Keywords Added**")
            if not add1.empty:
                st.dataframe(add1[["Campaign","Keyword","Match Type","P2 Installs"]].sort_values("P2 Installs", ascending=False),
                             use_container_width=True, hide_index=True)

    with tab2:
        bid2  = mar18[mar18["Change Type"] == "Bid Change"]
        add2  = mar18[mar18["Change Type"] == "Keyword Added"]
        drop2 = mar18[mar18["Change Type"] == "Keyword Dropped"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Bid Changes",      len(bid2))
        c2.metric("Keywords Added",   len(add2))
        c3.metric("Keywords Dropped", len(drop2))
        if not bid2.empty:
            st.markdown("**Bid Changes:**")
            st.dataframe(bid2[["Campaign","Keyword","Match Type","From","To","Direction","P2 Installs"]],
                         use_container_width=True, hide_index=True)
        if not drop2.empty:
            st.markdown("**Keywords Dropped:**")
            st.dataframe(drop2[["Campaign","Keyword","Match Type"]], use_container_width=True, hide_index=True)
        if not add2.empty:
            st.markdown(f"**{len(add2)} Keywords Added:**")
            st.dataframe(add2[["Campaign","Keyword","Match Type","P2 Installs"]].sort_values("P2 Installs", ascending=False),
                         use_container_width=True, hide_index=True)

    # ── Full filterable table ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Full Change Log — All 159 Events")
    c1, c2 = st.columns(2)
    type_sel = c1.multiselect("Change Type:", sorted(changelog["Change Type"].unique()),
                               default=sorted(changelog["Change Type"].unique()))
    camp_sel = c2.multiselect("Campaign:", sorted(changelog["Campaign"].dropna().unique()),
                               default=sorted(changelog["Campaign"].dropna().unique()))
    view = changelog[changelog["Change Type"].isin(type_sel) & changelog["Campaign"].isin(camp_sel)]
    st.dataframe(view[["Date","Change Type","Campaign","Keyword","Match Type","From","To","Direction","P2 Installs"]],
                 use_container_width=True, hide_index=True)

    # ── Impact summary ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Impact Assessment")
    st.markdown("""
**Feb 24 bid increases — mixed results:**
- Worked well (≥20 installs in P2): `review` (468), `shopify product reviews` (121), `reviews importer` (39), `reviews app` (35)
- Didn't help despite higher bid: `customer reviews` (4), `rivo reviews` (0), `loox - photo reviews` (0)
- Higher bids helped head terms; had little effect on niche competitor keywords

**Mar 18–Apr 15 adjustments:**
- `review widget` raised to $5.00 → 282 installs (strong)
- `review` raised again to $2.50 → 1,836 installs (top volume keyword)
- `google reviews` lowered $5.00→$4.00 (correct — $9.11 CPI)
- 7 Competitors keywords dropped (zero/low performers)

**Net result:** Weekly installs declined every week after Feb 24 — from **786/week** at peak to **~600/week** by early April (-24%).
Changes addressed expensive individual keywords but didn't reverse the macro decline. See **Diagnosis & Fix** for root causes.
""")


# ============================================================================
# MAIN
# ============================================================================

if not check_auth():
    st.stop()

# Load all data
daily        = load_daily()
yr_camps     = load_year_campaigns()
p2_camps     = load_p2_campaigns()
p1_kw        = load_keywords("p1")
p2_kw        = load_keywords("p2")
kw_comp      = build_kw_comparison(p1_kw, p2_kw)
country_df   = load_splits("q1_splits_country.csv")
device_df    = load_splits("q1_splits_device.csv")
plan_df      = load_splits("q1_splits_plan.csv")
search_df    = load_search_terms()
changelog_df = load_changelog()

# Sidebar
st.sidebar.title("⭐ Judge.me Ads")
st.sidebar.caption("Full Year: Apr 7, 2025 – Apr 7, 2026")
st.sidebar.markdown("**Daily detail:** Aug 21–Apr 15")
st.sidebar.markdown("**P2 snapshot:** Feb 24–Mar 17")
st.sidebar.markdown("**Splits:** Jan 8–Apr 7 (90d)")
st.sidebar.markdown("⚡ **Changes:** Feb 24 + Mar 18–Apr 15")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate:", [
    "📈 Overview",
    "📅 Trends & Timeline",
    "🎯 Campaign Breakdown",
    "🔑 Keywords",
    "🌍 Audience Splits",
    "🔍 Search Terms",
    "💡 Diagnosis & Fix",
    "📋 Change Log",
])

st.sidebar.markdown("---")
if not daily.empty:
    st.sidebar.caption(f"Daily rows: {len(daily):,}")
if not yr_camps.empty:
    st.sidebar.caption(f"Year campaigns: {len(yr_camps)}")
if not search_df.empty:
    st.sidebar.caption(f"Search terms: {len(search_df):,}")
if not changelog_df.empty:
    st.sidebar.caption(f"Change events: {len(changelog_df)}")

# Route
if page == "📈 Overview":
    page_overview(daily, yr_camps, p2_camps)
elif page == "📅 Trends & Timeline":
    page_trends(daily, p2_camps)
elif page == "🎯 Campaign Breakdown":
    page_campaigns(daily, yr_camps, p2_camps)
elif page == "🔑 Keywords":
    page_keywords(p1_kw, p2_kw, kw_comp)
elif page == "🌍 Audience Splits":
    page_splits(country_df, device_df, plan_df)
elif page == "🔍 Search Terms":
    page_search_terms(search_df, p2_kw)
elif page == "💡 Diagnosis & Fix":
    page_diagnosis(daily, yr_camps, p2_camps, p1_kw, p2_kw, country_df)
elif page == "📋 Change Log":
    page_changelog(changelog_df, daily)

st.markdown("---")
st.caption("Judge.me Ads Dashboard v3 · Apr 7 2025–Apr 7 2026 · Built with Streamlit")
