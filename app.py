import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K-Pop Chart Intelligence | Atlantic Records",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0d0f1a; color: #e8eaf6; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #0d0f1a 100%);
        border-right: 1px solid #2a2f50;
    }

    .metric-card {
        background: linear-gradient(135deg, #1e2340 0%, #252b4a 100%);
        border: 1px solid #3a4080;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-number {
        font-size: 2.4rem;
        font-weight: 700;
        color: #7c9fff;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #8891bb;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 6px;
    }
    .metric-sub {
        font-size: 0.72rem;
        color: #5a6490;
        margin-top: 3px;
    }

    .section-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #a0b4ff;
        border-left: 3px solid #5c7cfa;
        padding-left: 12px;
        margin: 8px 0 16px 0;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7c9fff, #b39dff, #ff8fab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #6b77a8;
        margin-top: 6px;
    }

    .insight-box {
        background: #1a2040;
        border-left: 3px solid #5c7cfa;
        border-radius: 0 8px 8px 0;
        padding: 10px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #c0caff;
    }

    div[data-testid="stTabs"] button {
        color: #6b77a8;
        font-size: 0.88rem;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #7c9fff;
        border-bottom-color: #7c9fff;
    }

    .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stRadio label { color: #8891bb !important; font-size: 0.82rem !important; }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    kpis   = pd.read_csv("song_kpis.csv")
    ra     = pd.read_csv("reentry_analysis.csv", parse_dates=["proper_date"])
    spikes = pd.read_csv("momentum_spikes.csv", parse_dates=["proper_date"])

    kpis["is_explicit"] = kpis["is_explicit"].astype(str).str.strip().str.lower()
    kpis["is_explicit_label"] = kpis["is_explicit"].map({"true":"Explicit","false":"Clean"}).fillna("Clean")
    ra["is_explicit_label"]   = ra["is_explicit"].astype(str).str.strip().str.lower().map({"true":"Explicit","false":"Clean"}).fillna("Clean")
    return kpis, ra, spikes

kpis, ra, spikes = load_data()

COLORS = {
    "primary":  "#7c9fff",
    "purple":   "#b39dff",
    "pink":     "#ff8fab",
    "teal":     "#4dd0e1",
    "green":    "#69f0ae",
    "bg":       "#0d0f1a",
    "card":     "#1e2340",
    "grid":     "#1e2340",
    "text":     "#e8eaf6",
    "muted":    "#6b77a8",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter"),
    xaxis=dict(gridcolor=COLORS["grid"], linecolor="#2a2f50", tickfont=dict(size=11)),
    yaxis=dict(gridcolor=COLORS["grid"], linecolor="#2a2f50", tickfont=dict(size=11)),
    margin=dict(t=40, b=40, l=40, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎵 K-Pop Intelligence")
    st.markdown("<div style='color:#5a6490;font-size:0.78rem;margin-bottom:20px'>Atlantic Recording Corporation<br>South Korea Market · 2024</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<div style='color:#8891bb;font-size:0.8rem;font-weight:600;margin-bottom:8px'>FILTERS</div>", unsafe_allow_html=True)

    album_filter = st.multiselect(
        "Album Type",
        options=kpis["album_type"].unique().tolist(),
        default=kpis["album_type"].unique().tolist()
    )

    explicit_filter = st.multiselect(
        "Content Type",
        options=["Clean", "Explicit"],
        default=["Clean", "Explicit"]
    )

    min_reentry = st.slider("Min Re-Entries", 0, int(kpis["total_reentries"].max()), 0)

    top_n = st.slider("Top N Artists / Songs", 5, 20, 10)

    st.divider()
    st.markdown("<div style='color:#5a6490;font-size:0.72rem'>Data: 27,800 records · 527 songs · 194 artists · May–Nov 2024</div>", unsafe_allow_html=True)

# ── FILTER DATA ───────────────────────────────────────────────────────────────
kf = kpis[
    kpis["album_type"].isin(album_filter) &
    kpis["is_explicit_label"].isin(explicit_filter) &
    (kpis["total_reentries"] >= min_reentry)
]

raf = ra[
    ra["album_type"].isin(album_filter) &
    ra["is_explicit_label"].isin(explicit_filter)
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:24px'>
    <div class='hero-title'>Comeback Momentum & Fandom Intensity</div>
    <div class='hero-sub'>South Korea Top 50 Spotify Playlist · Chart Re-Entry Intelligence · Atlantic Recording Corporation</div>
</div>
""", unsafe_allow_html=True)

# ── KPI METRICS ───────────────────────────────────────────────────────────────
reentries_only = raf[raf["entry_type"] == "reentry"]
total_reentries = len(reentries_only)
avg_gap = round(reentries_only["gap_days"].mean(), 1) if len(reentries_only) else 0
top_artist = kf.groupby("artist")["total_reentries"].sum().idxmax() if len(kf) else "—"
top_song_row = kf.nlargest(1, "fandom_intensity_score").iloc[0] if len(kf) else None
top_song = top_song_row["song"] if top_song_row is not None else "—"

c1, c2, c3, c4, c5 = st.columns(5)

def metric(col, number, label, sub):
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-number'>{number}</div>
        <div class='metric-label'>{label}</div>
        <div class='metric-sub'>{sub}</div>
    </div>""", unsafe_allow_html=True)

metric(c1, f"{total_reentries:,}", "Total Re-Entries", "Comeback events")
metric(c2, f"{avg_gap}d", "Avg Gap Before Return", "Days off chart")
metric(c3, f"{len(kf):,}", "Songs Analyzed", "After filters")
metric(c4, top_artist[:16]+"…" if len(top_artist)>16 else top_artist, "Top Comeback Artist", "Most re-entries")
metric(c5, top_song[:16]+"…" if len(top_song)>16 else top_song, "Highest Fandom Score", "Top ranked song")

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "📈  Re-Entry Timeline",
    "⚡  Momentum Spikes",
    "🏆  Fandom Leaderboard",
    "🎵  Content Analysis",
    "🔍  Song Explorer"
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — RE-ENTRY TIMELINE
# ═══════════════════════════════════════════════════════════════════
with t1:
    st.markdown("<div class='section-header'>Chart Re-Entry Activity Over Time</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        daily_reentries = (
            raf[raf["entry_type"] == "reentry"]
            .groupby("proper_date")
            .size()
            .reset_index(name="reentries")
        )
        if len(daily_reentries):
            daily_reentries["rolling_7d"] = daily_reentries["reentries"].rolling(7, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=daily_reentries["proper_date"], y=daily_reentries["reentries"],
                name="Daily Re-Entries", marker_color=COLORS["primary"], opacity=0.5
            ))
            fig.add_trace(go.Scatter(
                x=daily_reentries["proper_date"], y=daily_reentries["rolling_7d"],
                name="7-Day Average", line=dict(color=COLORS["pink"], width=2.5)
            ))
            fig.update_layout(**CHART_LAYOUT, title="Daily Re-Entry Events", height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Re-Entry Type Breakdown</div>", unsafe_allow_html=True)
        entry_counts = raf["entry_type"].value_counts().reset_index()
        entry_counts.columns = ["Type", "Count"]
        entry_counts["Type"] = entry_counts["Type"].str.replace("_", " ").str.title()
        fig2 = px.pie(
            entry_counts, names="Type", values="Count",
            color_discrete_sequence=[COLORS["primary"], COLORS["purple"], COLORS["teal"]],
            hole=0.55
        )
        fig2.update_layout(**{**CHART_LAYOUT, "margin": dict(t=20,b=20,l=20,r=20)}, height=320)
        fig2.update_traces(textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Top Songs by Re-Entry Count</div>", unsafe_allow_html=True)
    top_reentry_songs = (
        kf[kf["total_reentries"] > 0]
        .nlargest(top_n, "total_reentries")[["song","artist","album_type","total_reentries","total_days_on_chart","avg_popularity"]]
        .reset_index(drop=True)
    )
    top_reentry_songs.index += 1
    top_reentry_songs.columns = ["Song","Artist","Type","Re-Entries","Days on Chart","Avg Popularity"]

    fig3 = px.bar(
        top_reentry_songs, x="Re-Entries", y="Song", orientation="h",
        color="Re-Entries", color_continuous_scale=["#3a4080","#7c9fff","#b39dff"],
        text="Re-Entries"
    )
    fig3.update_traces(textposition="outside", textfont_size=11)
    fig3.update_layout(**CHART_LAYOUT, height=380)
    fig3.update_yaxes(autorange="reversed", gridcolor=COLORS["grid"])
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='insight-box'>💡 <b>Key Insight:</b> The top 3 artists — Lim Young Woong, Jimin, and NewJeans — account for 44.6% of all re-entry events, confirming comeback activity is driven by organized fandom strength rather than passive listener behavior.</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — MOMENTUM SPIKES
# ═══════════════════════════════════════════════════════════════════
with t2:
    st.markdown("<div class='section-header'>Momentum Spike Detection — Popularity Jump at Re-Entry</div>", unsafe_allow_html=True)

    spf = spikes[spikes["artist"].isin(kf["artist"].unique())] if len(kf) else spikes

    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            spf, x="gap_days", y="popularity_jump",
            color="album_type", size=spf["popularity_jump"].abs().fillna(2).clip(lower=2)+2,
            hover_data=["song","artist","popularity_jump","gap_days"],
            color_discrete_map={
                "single": COLORS["primary"],
                "album": COLORS["purple"],
                "compilation": COLORS["teal"]
            },
            labels={"gap_days":"Days Off Chart","popularity_jump":"Popularity Jump at Re-Entry"},
            title="Momentum Spike vs Days Off Chart"
        )
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS["muted"], opacity=0.5)
        fig.update_layout(**CHART_LAYOUT, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_spikes = spf.nlargest(top_n, "popularity_jump")[["song","artist","popularity_jump","gap_days","album_type"]].reset_index(drop=True)
        top_spikes.index += 1
        fig2 = px.bar(
            top_spikes, x="popularity_jump", y="song", orientation="h",
            color="popularity_jump",
            color_continuous_scale=["#3a4080","#7c9fff","#69f0ae"],
            text="popularity_jump",
            title=f"Top {top_n} Momentum Spikes"
        )
        fig2.update_traces(textposition="outside", textfont_size=10)
        fig2.update_layout(**CHART_LAYOUT, height=360)
        fig2.update_yaxes(autorange="reversed")
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Popularity Jump Distribution</div>", unsafe_allow_html=True)
    fig3 = px.histogram(
        spf, x="popularity_jump", nbins=40,
        color_discrete_sequence=[COLORS["purple"]],
        title="Distribution of Popularity Jumps at Re-Entry",
        labels={"popularity_jump":"Popularity Jump"}
    )
    fig3.add_vline(x=0, line_dash="dash", line_color=COLORS["pink"], annotation_text="Baseline (0)")
    fig3.update_layout(**CHART_LAYOUT, height=280)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='insight-box'>💡 <b>Key Insight:</b> The highest recorded momentum spike was +87 points (Travis Scott's K-POP, after just 3 days off chart), followed by LE SSERAFIM's Smart at +47 after 2 days — both consistent with scheduled promotional activations rather than organic listener return.</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — FANDOM LEADERBOARD
# ═══════════════════════════════════════════════════════════════════
with t3:
    st.markdown("<div class='section-header'>Fandom Intensity Leaderboard</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        top_songs_fi = kf.nlargest(top_n, "fandom_intensity_score")[["song","artist","fandom_intensity_score","total_reentries","total_days_on_chart"]].reset_index(drop=True)
        top_songs_fi.index += 1
        fig = px.bar(
            top_songs_fi, x="fandom_intensity_score", y="song", orientation="h",
            color="fandom_intensity_score",
            color_continuous_scale=["#2e1f5e","#7c9fff","#b39dff","#ff8fab"],
            text=top_songs_fi["fandom_intensity_score"].round(1),
            title=f"Top {top_n} Songs by Fandom Intensity Score"
        )
        fig.update_traces(textposition="outside", textfont_size=10)
        fig2.update_layout(**CHART_LAYOUT, height=400)
        fig2.update_yaxes(autorange="reversed")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_artists_fi = (
            kf.groupby("artist")
            .agg(total_reentries=("total_reentries","sum"), fandom_score=("fandom_intensity_score","mean"), songs=("song","count"))
            .reset_index()
            .nlargest(top_n, "total_reentries")
        )
        fig2 = px.bar(
            top_artists_fi, x="total_reentries", y="artist", orientation="h",
            color="fandom_score",
            color_continuous_scale=["#3a4080","#7c9fff","#ff8fab"],
            text="total_reentries",
            title=f"Top {top_n} Artists by Total Re-Entries"
        )
        fig2.update_traces(textposition="outside", textfont_size=10)
        fig2.update_layout(**CHART_LAYOUT, height=400)
        fig2.update_yaxes(autorange="reversed")
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Fandom Score vs Days on Chart</div>", unsafe_allow_html=True)
    fig3 = px.scatter(
        kf, x="total_days_on_chart", y="fandom_intensity_score",
        color="album_type", size="total_reentries",
        hover_data=["song","artist"],
        color_discrete_map={"single": COLORS["primary"], "album": COLORS["purple"], "compilation": COLORS["teal"]},
        labels={"total_days_on_chart":"Days on Chart","fandom_intensity_score":"Fandom Intensity Score"},
        title="Fandom Intensity Score vs Chart Presence"
    )
    fig3.update_layout(**CHART_LAYOUT, height=320)
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 4 — CONTENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with t4:
    st.markdown("<div class='section-header'>Singles vs Albums vs Compilations</div>", unsafe_allow_html=True)

    album_summary = kf.groupby("album_type").agg(
        songs=("song","count"),
        avg_reentries=("total_reentries","mean"),
        avg_days=("total_days_on_chart","mean"),
        avg_popularity=("avg_popularity","mean"),
        avg_fandom=("fandom_intensity_score","mean")
    ).reset_index().round(2)

    col1, col2, col3 = st.columns(3)
    metrics_list = [
        ("avg_reentries","Avg Re-Entries","Re-Entry Frequency"),
        ("avg_days","Avg Days on Chart","Chart Longevity"),
        ("avg_fandom","Avg Fandom Score","Fandom Intensity"),
    ]
    for col, (metric_col, title, ylabel) in zip([col1,col2,col3], metrics_list):
        with col:
            fig = px.bar(
                album_summary, x="album_type", y=metric_col,
                color="album_type",
                color_discrete_map={"single": COLORS["primary"], "album": COLORS["purple"], "compilation": COLORS["teal"]},
                text=album_summary[metric_col].round(1),
                title=title
            )
            fig.update_traces(textposition="outside", textfont_size=11)
            fig.update_layout(**{**CHART_LAYOUT, "showlegend": False}, height=300)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Explicit vs Clean Content Performance</div>", unsafe_allow_html=True)

    explicit_summary = kf.groupby("is_explicit_label").agg(
        songs=("song","count"),
        avg_reentries=("total_reentries","mean"),
        avg_days=("total_days_on_chart","mean"),
        avg_fandom=("fandom_intensity_score","mean")
    ).reset_index().round(2)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            explicit_summary, x="is_explicit_label", y="avg_reentries",
            color="is_explicit_label",
            color_discrete_map={"Clean": COLORS["teal"], "Explicit": COLORS["pink"]},
            text=explicit_summary["avg_reentries"].round(2),
            title="Avg Re-Entries: Clean vs Explicit",
            labels={"is_explicit_label":"Content Type","avg_reentries":"Avg Re-Entries"}
        )
        fig.update_traces(textposition="outside", textfont_size=12)
        fig.update_layout(**{**CHART_LAYOUT,"showlegend":False}, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            explicit_summary, x="is_explicit_label", y="avg_days",
            color="is_explicit_label",
            color_discrete_map={"Clean": COLORS["teal"], "Explicit": COLORS["pink"]},
            text=explicit_summary["avg_days"].round(1),
            title="Avg Days on Chart: Clean vs Explicit",
            labels={"is_explicit_label":"Content Type","avg_days":"Avg Days on Chart"}
        )
        fig2.update_traces(textposition="outside", textfont_size=12)
        fig2.update_layout(**{**CHART_LAYOUT,"showlegend":False}, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='insight-box'>💡 <b>Key Insight:</b> Clean content averaged 2.27 re-entries vs just 0.63 for explicit tracks — a 260% gap. Non-explicit songs also stayed on chart 56.8 days on average vs 27.1 days for explicit content. This reflects the clean-image culture at the core of K-Pop fandom engagement.</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 5 — SONG EXPLORER
# ═══════════════════════════════════════════════════════════════════
with t5:
    st.markdown("<div class='section-header'>Song Explorer — Re-Entry Timeline for Any Song</div>", unsafe_allow_html=True)

    song_list = sorted(ra["song"].unique().tolist())
    selected_song = st.selectbox("Select a Song", song_list)

    song_data = ra[ra["song"] == selected_song].sort_values("proper_date")
    song_kpi  = kpis[kpis["song"] == selected_song]

    if len(song_data):
        col1, col2, col3, col4 = st.columns(4)
        reentries_count = len(song_data[song_data["entry_type"]=="reentry"])
        days_count = len(song_data)
        avg_pop = round(song_data["popularity"].mean(), 1)
        artist_name = song_data["artist"].iloc[0]

        metric(col1, reentries_count, "Re-Entries", "Total comebacks")
        metric(col2, days_count, "Days on Chart", "Total presence")
        metric(col3, avg_pop, "Avg Popularity", "0–100 score")
        metric(col4, song_kpi["fandom_intensity_score"].values[0].round(1) if len(song_kpi) else "—", "Fandom Score", "Composite KPI")

        st.markdown("<br>", unsafe_allow_html=True)

        color_map = {"first_entry": COLORS["teal"], "reentry": COLORS["pink"], "continuing": COLORS["primary"]}

        fig = go.Figure()
        for etype, color in color_map.items():
            subset = song_data[song_data["entry_type"]==etype]
            if len(subset):
                fig.add_trace(go.Scatter(
                    x=subset["proper_date"], y=subset["popularity"],
                    mode="markers",
                    name=etype.replace("_"," ").title(),
                    marker=dict(color=color, size=8),
                ))

        fig.update_layout(
            **CHART_LAYOUT,
            title=f"Popularity Timeline — {selected_song} ({artist_name})",
            xaxis_title="Date", yaxis_title="Popularity Score",
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='section-header'>Chart Position Over Time</div>", unsafe_allow_html=True)
        fig2 = px.line(
            song_data, x="proper_date", y="position",
            title=f"Chart Position — {selected_song}",
            labels={"proper_date":"Date","position":"Chart Position (1=Best)"},
            color_discrete_sequence=[COLORS["purple"]]
        )
        fig2.update_yaxes(autorange="reversed")
        fig2.update_layout(**CHART_LAYOUT, height=300)
        st.plotly_chart(fig2, use_container_width=True)

        reentry_events = song_data[song_data["entry_type"]=="reentry"][["proper_date","position","popularity","gap_days"]].reset_index(drop=True)
        reentry_events.index += 1
        if len(reentry_events):
            st.markdown("<div class='section-header'>Re-Entry Events Detail</div>", unsafe_allow_html=True)
            reentry_events.columns = ["Re-Entry Date","Position","Popularity","Days Off Chart"]
            st.dataframe(reentry_events, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;color:#3a4060;font-size:0.75rem;padding:8px'>
    Atlantic Recording Corporation · South Korea Top 50 Analysis · 2024 · Built with Streamlit
</div>
""", unsafe_allow_html=True)
