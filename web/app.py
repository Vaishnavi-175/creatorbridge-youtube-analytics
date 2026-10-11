from __future__ import annotations

from pathlib import Path
import html

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from web.utils.validation import validate_dataframe
except ImportError:
    from utils.validation import validate_dataframe


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CreatorBridge",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "generated"

DATA_FILES = {
    "creators": "creators.csv",
    "channels": "channels.csv",
    "videos": "videos.csv",
    "video_metrics": "video_metrics.csv",
    "audience": "audience.csv",
    "brands": "brands.csv",
    "campaigns": "campaigns.csv",
    "campaign_creators": "campaign_creators.csv",
    "campaign_performance": "campaign_performance.csv",
    "creator_scores": "final_creator_scores.csv",
}

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f1f5f9;
    }
    [data-testid="stSidebar"] {
        background-color: #151923;
    }
    .hero {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(120deg, #202b48, #34214c);
        border: 1px solid #41496b;
        margin-bottom: 20px;
    }
    .hero h1 {
        margin: 0;
        color: white;
    }
    .hero p {
        color: #d1d5db;
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

@st.cache_data
def read_csv_file(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_data():
    data = {}
    errors = []

    for key, filename in DATA_FILES.items():
        filepath = DATA_PATH / filename

        if not filepath.exists():
            data[key] = pd.DataFrame()
            errors.append(f"Missing file: {filename}")
            continue

        try:
            data[key] = read_csv_file(str(filepath))
        except Exception as exc:
            data[key] = pd.DataFrame()
            errors.append(f"{filename}: {exc}")

    return data, errors


def find_col(df: pd.DataFrame, candidates: list[str]):
    """Return the first matching column, ignoring case."""
    lookup = {str(col).lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def numeric_col(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    col = find_col(df, candidates)

    if col is None:
        return pd.Series(0, index=df.index, dtype=float)

    return pd.to_numeric(df[col], errors="coerce").fillna(0)


def text_col(
    df: pd.DataFrame,
    candidates: list[str],
    default: str = "Unknown",
) -> pd.Series:
    col = find_col(df, candidates)

    if col is None:
        return pd.Series(default, index=df.index, dtype="object")

    return df[col].fillna(default).astype(str)


def safe_pct(numerator, denominator):
    try:
        if denominator == 0:
            return 0.0
        return float(numerator) / float(denominator) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def metric_sum(df, candidates):
    return float(numeric_col(df, candidates).sum())


def show_table(df: pd.DataFrame, height: int = 380):
    if df.empty:
        st.info("No data available for this view.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height,
    )


def show_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=45, b=10),
        font=dict(color="#e5e7eb"),
    )
    st.plotly_chart(fig, use_container_width=True)


def section_title(title, description=None):
    st.subheader(title)
    if description:
        st.caption(description)


def make_display_names(df):
    name_col = find_col(
        df,
        ["creator_name", "name", "channel_name", "creator", "username"],
    )
    id_col = find_col(df, ["creator_id", "channel_id", "id"])

    if name_col and id_col:
        return (
            df[name_col].fillna("Unknown").astype(str)
            + " ("
            + df[id_col].astype(str)
            + ")"
        )

    if name_col:
        return df[name_col].fillna("Unknown").astype(str)

    if id_col:
        return df[id_col].astype(str)

    return pd.Series(
        [f"Creator {i + 1}" for i in range(len(df))],
        index=df.index,
    )


def merge_video_data(videos, metrics, channels, creators):
    """Join video metadata with its separate performance metrics."""
    if videos.empty:
        return pd.DataFrame()

    result = videos.copy()

    if (
        not metrics.empty
        and "video_id" in result.columns
        and "video_id" in metrics.columns
    ):
        metric_copy = metrics.copy()

        # Avoid accidental duplicate metric columns.
        duplicate_cols = [
            col for col in metric_copy.columns
            if col != "video_id" and col in result.columns
        ]
        metric_copy = metric_copy.drop(columns=duplicate_cols)

        result = result.merge(
            metric_copy,
            on="video_id",
            how="left",
            validate="one_to_one",
        )

    if (
        not channels.empty
        and "channel_id" in result.columns
        and {"channel_id", "creator_id"}.issubset(channels.columns)
    ):
        channel_lookup = channels[
            ["channel_id", "creator_id"]
        ].drop_duplicates("channel_id")

        if "creator_id" not in result.columns:
            result = result.merge(
                channel_lookup,
                on="channel_id",
                how="left",
            )

    if (
        not creators.empty
        and "creator_id" in result.columns
        and "creator_id" in creators.columns
    ):
        name_col = find_col(
            creators,
            ["creator_name", "name", "username"],
        )

        if name_col and name_col != "creator_id":
            creator_lookup = creators[
                ["creator_id", name_col]
            ].drop_duplicates("creator_id")

            if name_col not in result.columns:
                result = result.merge(
                    creator_lookup,
                    on="creator_id",
                    how="left",
                )

    return result


def build_creator_data(creators, scores, channels):
    """Combine creator profile information and scoring data."""
    if creators.empty:
        result = scores.copy()
    else:
        result = creators.copy()

        if (
            not scores.empty
            and "creator_id" in result.columns
            and "creator_id" in scores.columns
        ):
            score_copy = scores.copy()
            duplicate_cols = [
                col for col in score_copy.columns
                if col != "creator_id" and col in result.columns
            ]
            score_copy = score_copy.drop(columns=duplicate_cols)

            result = result.merge(
                score_copy,
                on="creator_id",
                how="left",
                validate="one_to_one",
            )

    if (
        not channels.empty
        and "creator_id" in result.columns
        and "creator_id" in channels.columns
    ):
        channel_count = (
            channels.groupby("creator_id")
            .size()
            .rename("channel_count")
            .reset_index()
        )

        if "channel_count" not in result.columns:
            result = result.merge(
                channel_count,
                on="creator_id",
                how="left",
            )

    return result


def build_campaign_data(campaigns, campaign_creators, performance, creators):
    """Join campaign assignments and available campaign performance."""
    if campaign_creators.empty:
        result = performance.copy()
    else:
        result = campaign_creators.copy()

        if (
            not performance.empty
            and "campaign_id" in result.columns
            and "campaign_id" in performance.columns
        ):
            join_keys = ["campaign_id"]

            if (
                "creator_id" in result.columns
                and "creator_id" in performance.columns
            ):
                join_keys.append("creator_id")

            perf_copy = performance.copy()
            duplicate_cols = [
                col for col in perf_copy.columns
                if col not in join_keys and col in result.columns
            ]
            perf_copy = perf_copy.drop(columns=duplicate_cols)

            result = result.merge(
                perf_copy,
                on=join_keys,
                how="left",
            )

    if (
        not campaigns.empty
        and "campaign_id" in result.columns
        and "campaign_id" in campaigns.columns
    ):
        campaign_lookup = campaigns.copy()
        duplicate_cols = [
            col for col in campaign_lookup.columns
            if col != "campaign_id" and col in result.columns
        ]
        campaign_lookup = campaign_lookup.drop(columns=duplicate_cols)

        result = result.merge(
            campaign_lookup.drop_duplicates("campaign_id"),
            on="campaign_id",
            how="left",
        )

    if (
        not creators.empty
        and "creator_id" in result.columns
        and "creator_id" in creators.columns
    ):
        name_col = find_col(creators, ["creator_name", "name", "username"])

        if name_col and name_col not in result.columns:
            creator_lookup = creators[
                ["creator_id", name_col]
            ].drop_duplicates("creator_id")

            result = result.merge(
                creator_lookup,
                on="creator_id",
                how="left",
            )

    return result


def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD AND PREPARE DATA
# ============================================================

data, load_errors = load_data()

creators = data["creators"]
channels = data["channels"]
videos = data["videos"]
video_metrics = data["video_metrics"]
audience = data["audience"]
brands = data["brands"]
campaigns = data["campaigns"]
campaign_creators = data["campaign_creators"]
campaign_performance = data["campaign_performance"]
creator_scores = data["creator_scores"]

creator_data = build_creator_data(
    creators,
    creator_scores,
    channels,
)

video_data = merge_video_data(
    videos,
    video_metrics,
    channels,
    creators,
)

campaign_data = build_campaign_data(
    campaigns,
    campaign_creators,
    campaign_performance,
    creators,
)

if not creator_data.empty:
    creator_data = creator_data.loc[
        :, ~creator_data.columns.duplicated()
    ]

if not video_data.empty:
    video_data = video_data.loc[
        :, ~video_data.columns.duplicated()
    ]

if not campaign_data.empty:
    campaign_data = campaign_data.loc[
        :, ~campaign_data.columns.duplicated()
    ]


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("✨ CreatorBridge")
st.sidebar.caption("Creator Marketing Intelligence Platform")

pages = [
    "Executive Overview",
    "Creator Discovery",
    "Creator 360",
    "Brand Match",
    "Emerging Creators",
    "Campaign Intelligence",
    "Campaign Simulator",
    "Content Intelligence",
    "Audience Intelligence",
    "Creator Comparison",
    "Performance Flags",
    "Data Quality",
]

page = st.sidebar.radio("Navigate", pages)

st.sidebar.divider()
st.sidebar.caption("Built with Python, Pandas, Streamlit & Plotly")


# ============================================================
# 1. EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":
    hero(
        "CreatorBridge",
        "A unified view of creators, content, audience and campaigns.",
    )

    total_creators = (
        creator_data["creator_id"].nunique()
        if "creator_id" in creator_data.columns
        else len(creator_data)
    )
    total_videos = len(video_data)
    total_campaigns = (
        campaigns["campaign_id"].nunique()
        if "campaign_id" in campaigns.columns
        else len(campaigns)
    )
    total_views = metric_sum(video_data, ["views", "view_count"])
    total_likes = metric_sum(video_data, ["likes", "like_count"])
    total_comments = metric_sum(video_data, ["comments", "comment_count"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Creators", f"{total_creators:,}")
    c2.metric("Videos", f"{total_videos:,}")
    c3.metric("Campaigns", f"{total_campaigns:,}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Total Views", f"{total_views:,.0f}")
    c5.metric("Total Likes", f"{total_likes:,.0f}")
    c6.metric("Total Comments", f"{total_comments:,.0f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        section_title("Creators by Category")

        category_col = find_col(
            creator_data,
            ["category", "niche", "creator_category"],
        )

        if category_col:
            counts = (
                creator_data[category_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .reset_index()
            )
            counts.columns = ["Category", "Creators"]

            fig = px.bar(
                counts,
                x="Category",
                y="Creators",
                title="Creator Distribution",
            )
            show_chart(fig)
        else:
            st.info("No creator category column was found.")

    with right:
        section_title("Video Performance")

        if not video_data.empty:
            chart_data = pd.DataFrame({
                "Metric": ["Views", "Likes", "Comments", "Shares"],
                "Total": [
                    metric_sum(video_data, ["views"]),
                    metric_sum(video_data, ["likes"]),
                    metric_sum(video_data, ["comments"]),
                    metric_sum(video_data, ["shares"]),
                ],
            })

            fig = px.bar(
                chart_data,
                x="Metric",
                y="Total",
                title="Total Content Engagement",
            )
            show_chart(fig)
        else:
            st.info("Video data is not available.")

    section_title("Creator Snapshot")
    show_table(creator_data.head(10))


# ============================================================
# 2. CREATOR DISCOVERY
# ============================================================

elif page == "Creator Discovery":
    hero(
        "Creator Discovery",
        "Search and filter creators using the available profile data.",
    )

    if creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        search = st.text_input("Search creator by name or ID")

        category_col = find_col(
            creator_data,
            ["category", "niche", "creator_category"],
        )
        location_col = find_col(
            creator_data,
            ["location", "city", "country"],
        )

        filtered = creator_data.copy()

        if search:
            mask = filtered.astype(str).apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            ).any(axis=1)
            filtered = filtered[mask]

        f1, f2 = st.columns(2)

        if category_col:
            categories = sorted(
                filtered[category_col]
                .dropna()
                .astype(str)
                .unique()
            )
            with f1:
                selected_categories = st.multiselect(
                    "Category",
                    categories,
                    default=categories,
                )
            filtered = filtered[
                filtered[category_col].astype(str).isin(
                    selected_categories
                )
            ]

        if location_col:
            locations = sorted(
                filtered[location_col]
                .dropna()
                .astype(str)
                .unique()
            )
            with f2:
                selected_locations = st.multiselect(
                    "Location",
                    locations,
                    default=locations,
                )
            filtered = filtered[
                filtered[location_col].astype(str).isin(
                    selected_locations
                )
            ]

        st.metric("Matching Creators", len(filtered))
        show_table(filtered)


# ============================================================
# 3. CREATOR 360
# ============================================================

elif page == "Creator 360":
    hero(
        "Creator 360",
        "Explore one creator's profile, content and available metrics.",
    )

    if creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        display_names = make_display_names(creator_data)
        selected_label = st.selectbox(
            "Select Creator",
            display_names.tolist(),
        )
        selected_index = display_names[
            display_names == selected_label
        ].index[0]

        creator = creator_data.loc[selected_index]
        creator_id_col = find_col(creator_data, ["creator_id"])
        creator_id = (
            creator[creator_id_col]
            if creator_id_col
            else None
        )

        st.subheader(str(selected_label))

        profile_fields = [
            col for col in creator_data.columns
            if col not in ["creator_id"]
        ]

        profile = creator[profile_fields].to_frame("Value")
        profile.index.name = "Field"
        show_table(profile.reset_index(), height=300)

        if (
            creator_id is not None
            and "creator_id" in video_data.columns
        ):
            creator_videos = video_data[
                video_data["creator_id"].astype(str)
                == str(creator_id)
            ]

            a, b, c = st.columns(3)
            a.metric("Videos", len(creator_videos))
            b.metric(
                "Views",
                f"{metric_sum(creator_videos, ['views']):,.0f}",
            )
            c.metric(
                "Likes",
                f"{metric_sum(creator_videos, ['likes']):,.0f}",
            )

            section_title("Creator's Videos")
            show_table(creator_videos)


# ============================================================
# 4. BRAND MATCH
# ============================================================

elif page == "Brand Match":
    hero(
        "Brand Match",
        "Find creators whose category and available profile information fit a brand.",
    )

    if brands.empty:
        st.warning("Brand data is not available.")
    elif creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        brand_name_col = find_col(
            brands,
            ["brand_name", "name", "brand"],
        )
        brand_category_col = find_col(
            brands,
            ["category", "industry", "product_category", "niche"],
        )
        creator_category_col = find_col(
            creator_data,
            ["category", "niche", "creator_category"],
        )

        brand_labels = make_display_names(brands)
        selected_brand_label = st.selectbox(
            "Choose Brand",
            brand_labels.tolist(),
        )
        brand_idx = brand_labels[
            brand_labels == selected_brand_label
        ].index[0]
        brand = brands.loc[brand_idx]

        st.write("**Selected brand details**")
        show_table(brand.to_frame("Value").reset_index().rename(
            columns={"index": "Field"}
        ))

        matches = creator_data.copy()
        matched_by_category = False

        if brand_category_col and creator_category_col:
            brand_category = str(
                brand[brand_category_col]
            ).strip().lower()

            category_matches = matches[
                matches[creator_category_col]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(brand_category, regex=False)
            ]

            if brand_category and not category_matches.empty:
                matches = category_matches
                matched_by_category = True

        score_col = find_col(
            matches,
            [
                "final_score",
                "creator_score",
                "overall_score",
                "score",
                "creator_performance_score",
            ],
        )

        if score_col:
            matches[score_col] = pd.to_numeric(
                matches[score_col],
                errors="coerce",
            )
            matches = matches.sort_values(
                score_col,
                ascending=False,
                na_position="last",
            )

        if matched_by_category:
            st.caption("Results filtered by matching category.")
        else:
            st.caption(
                "No exact category match was found; showing creators "
                "ranked by available score or profile data."
            )

        st.metric("Suggested Creators", len(matches))
        show_table(matches.head(20))


# ============================================================
# 5. EMERGING CREATORS
# ============================================================

elif page == "Emerging Creators":
    hero(
        "Emerging Creators",
        "Identify creators with promising performance using available metrics.",
    )

    if creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        emerging = creator_data.copy()

        score_col = find_col(
            emerging,
            [
                "final_score",
                "creator_score",
                "overall_score",
                "score",
                "creator_performance_score",
            ],
        )
        followers_col = find_col(
            emerging,
            ["followers", "follower_count", "subscribers"],
        )

        if score_col:
            emerging[score_col] = pd.to_numeric(
                emerging[score_col],
                errors="coerce",
            )
            emerging = emerging.sort_values(
                score_col,
                ascending=False,
                na_position="last",
            )
            st.caption(
                "Ranked by the available creator score. "
                "This is a ranking, not a forecast."
            )
        elif followers_col:
            emerging[followers_col] = pd.to_numeric(
                emerging[followers_col],
                errors="coerce",
            )
            emerging = emerging.sort_values(
                followers_col,
                ascending=True,
                na_position="last",
            )
            st.caption(
                "Ranked by follower count, lowest first. "
                "Follower count alone does not establish growth."
            )
        else:
            st.caption(
                "No score or follower field was found. "
                "Showing the available creator profiles."
            )

        show_table(emerging.head(25))


# ============================================================
# 6. CAMPAIGN INTELLIGENCE
# ============================================================

elif page == "Campaign Intelligence":
    hero(
        "Campaign Intelligence",
        "Review campaign assignments and performance metrics.",
    )

    if campaign_data.empty:
        st.warning(
            "Campaign data is unavailable. Check campaign CSV files."
        )
    else:
        c1, c2, c3 = st.columns(3)

        campaign_id_col = find_col(campaign_data, ["campaign_id"])
        creator_id_col = find_col(campaign_data, ["creator_id"])

        c1.metric(
            "Campaigns",
            campaign_data[campaign_id_col].nunique()
            if campaign_id_col else len(campaign_data),
        )
        c2.metric(
            "Creator Assignments",
            campaign_data[creator_id_col].nunique()
            if creator_id_col else len(campaign_data),
        )
        c3.metric(
            "Tracked Views",
            f"{metric_sum(campaign_data, ['views']):,.0f}",
        )

        campaign_name_col = find_col(
            campaign_data,
            ["campaign_name", "name"],
        )

        if campaign_name_col:
            campaign_options = sorted(
                campaign_data[campaign_name_col]
                .dropna()
                .astype(str)
                .unique()
            )
            selected = st.selectbox(
                "Filter Campaign",
                ["All"] + campaign_options,
            )

            if selected != "All":
                campaign_data_view = campaign_data[
                    campaign_data[campaign_name_col].astype(str)
                    == selected
                ]
            else:
                campaign_data_view = campaign_data
        else:
            campaign_data_view = campaign_data

        left, right = st.columns(2)

        with left:
            st.metric(
                "Likes",
                f"{metric_sum(campaign_data_view, ['likes']):,.0f}",
            )
            st.metric(
                "Comments",
                f"{metric_sum(campaign_data_view, ['comments']):,.0f}",
            )

        with right:
            st.metric(
                "Conversions",
                f"{metric_sum(campaign_data_view, ['conversions']):,.0f}",
            )
            st.metric(
                "Revenue",
                money(metric_sum(campaign_data_view, ["revenue"])),
            )

        show_table(campaign_data_view)


# ============================================================
# 7. CAMPAIGN SIMULATOR
# ============================================================

elif page == "Campaign Simulator":
    hero(
        "Campaign Simulator",
        "Build an illustrative creator shortlist within a budget.",
    )

    if creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        cost_col = find_col(
            creator_data,
            ["estimated_cost", "cost", "rate", "price", "agreed_cost"],
        )
        creator_id_col = find_col(creator_data, ["creator_id"])
        score_col = find_col(
            creator_data,
            [
                "final_score",
                "creator_score",
                "overall_score",
                "score",
                "creator_performance_score",
            ],
        )

        budget = st.number_input(
            "Campaign Budget (₹)",
            min_value=0,
            value=100000,
            step=5000,
        )

        if cost_col:
            costs = pd.to_numeric(
                creator_data[cost_col],
                errors="coerce",
            ).fillna(0)
            st.caption(f"Creator cost uses the available `{cost_col}` field.")
        else:
            costs = pd.Series(
                10000.0,
                index=creator_data.index,
            )
            st.caption(
                "No cost field was found. For this demo only, "
                "each creator is assigned an illustrative cost of ₹10,000."
            )

        options = make_display_names(creator_data)
        selected = st.multiselect(
            "Select creators",
            options.tolist(),
            default=options.head(min(5, len(options))).tolist(),
        )

        selected_indices = options[options.isin(selected)].index
        simulation = creator_data.loc[selected_indices].copy()
        simulation["Estimated Cost"] = costs.loc[selected_indices]

        if score_col:
            simulation["Available Score"] = pd.to_numeric(
                simulation[score_col],
                errors="coerce",
            )

        estimated_total = float(simulation["Estimated Cost"].sum())
        remaining = float(budget - estimated_total)

        a, b, c = st.columns(3)
        a.metric("Selected Creators", len(simulation))
        b.metric("Estimated Cost", money(estimated_total))
        c.metric("Budget Remaining", money(remaining))

        if estimated_total > budget:
            st.warning("Selected creators exceed the entered budget.")
        else:
            st.success("Selected creators fit within the entered budget.")

        st.caption(
            "This is a planning aid, not a prediction of actual campaign results."
        )
        show_table(simulation)


# ============================================================
# 8. CONTENT INTELLIGENCE
# ============================================================

elif page == "Content Intelligence":
    hero(
        "Content Intelligence",
        "Explore video categories, formats and performance.",
    )

    if video_data.empty:
        st.warning("Video data is not available.")
    else:
        category_col = find_col(
            video_data,
            ["category", "video_category", "niche"],
        )
        type_col = find_col(
            video_data,
            ["video_type", "content_type", "format"],
        )

        f1, f2 = st.columns(2)
        filtered = video_data.copy()

        if category_col:
            categories = sorted(
                filtered[category_col].dropna().astype(str).unique()
            )
            with f1:
                chosen_categories = st.multiselect(
                    "Video Category",
                    categories,
                    default=categories,
                )
            filtered = filtered[
                filtered[category_col].astype(str).isin(chosen_categories)
            ]

        if type_col:
            types = sorted(
                filtered[type_col].dropna().astype(str).unique()
            )
            with f2:
                chosen_types = st.multiselect(
                    "Video Type",
                    types,
                    default=types,
                )
            filtered = filtered[
                filtered[type_col].astype(str).isin(chosen_types)
            ]

        view_col = find_col(filtered, ["views"])
        if category_col and view_col:
            chart_data = filtered.copy()
            chart_data[view_col] = pd.to_numeric(
                chart_data[view_col],
                errors="coerce",
            ).fillna(0)

            summary = (
                chart_data.groupby(category_col, dropna=False)[view_col]
                .sum()
                .reset_index()
                .sort_values(view_col, ascending=False)
            )

            fig = px.bar(
                summary,
                x=category_col,
                y=view_col,
                title="Views by Category",
            )
            show_chart(fig)

        show_table(filtered)


# ============================================================
# 9. AUDIENCE INTELLIGENCE
# ============================================================

elif page == "Audience Intelligence":
    hero(
        "Audience Intelligence",
        "Explore audience segments using the available audience dataset.",
    )

    if audience.empty:
        st.warning("Audience data is not available.")
    else:
        st.metric("Audience Records", len(audience))

        segment_col = find_col(
            audience,
            ["age_group", "gender", "location", "country", "city"],
        )
        share_col = find_col(
            audience,
            [
                "audience_percentage",
                "percentage",
                "share",
                "audience_share",
                "percentage_of_audience",
            ],
        )

        if segment_col:
            segments = sorted(
                audience[segment_col].dropna().astype(str).unique()
            )
            selected_segments = st.multiselect(
                "Filter Audience Segment",
                segments,
                default=segments,
            )
            audience_view = audience[
                audience[segment_col].astype(str).isin(selected_segments)
            ]
        else:
            audience_view = audience

        if segment_col and share_col:
            chart_data = audience_view.copy()
            chart_data[share_col] = pd.to_numeric(
                chart_data[share_col],
                errors="coerce",
            ).fillna(0)

            fig = px.bar(
                chart_data,
                x=segment_col,
                y=share_col,
                title="Audience Distribution",
            )
            show_chart(fig)

        show_table(audience_view)


# ============================================================
# 10. CREATOR COMPARISON
# ============================================================

elif page == "Creator Comparison":
    hero(
        "Creator Comparison",
        "Compare creator profiles and their available performance scores.",
    )

    if creator_data.empty:
        st.warning("Creator data is not available.")
    else:
        options = make_display_names(creator_data).tolist()
        selected = st.multiselect(
            "Choose creators to compare",
            options,
            default=options[: min(3, len(options))],
        )

        display_names = make_display_names(creator_data)
        comparison_indices = display_names[
            display_names.isin(selected)
        ].index

        comparison = creator_data.loc[comparison_indices].copy()

        if comparison.empty:
            st.info("Select at least one creator to compare.")
        else:
            show_table(comparison)

            score_col = find_col(
                comparison,
                [
                    "final_score",
                    "creator_score",
                    "overall_score",
                    "score",
                    "creator_performance_score",
                ],
            )

            if score_col:
                plot_df = comparison.copy()
                plot_df["Display Name"] = make_display_names(plot_df)
                plot_df[score_col] = pd.to_numeric(
                    plot_df[score_col],
                    errors="coerce",
                ).fillna(0)

                fig = px.bar(
                    plot_df,
                    x="Display Name",
                    y=score_col,
                    title="Creator Score Comparison",
                )
                show_chart(fig)
            else:
                st.info(
                    "No standard creator score column was found. "
                    "Use the table to compare available fields."
                )


# ============================================================
# 11. PERFORMANCE FLAGS
# ============================================================

elif page == "Performance Flags":
    hero(
        "Performance Flags",
        "Check for missing metrics, low engagement and unusual data values.",
    )

    flags = []

    for dataset_name, df in data.items():
        if df.empty:
            flags.append({
                "Dataset": dataset_name,
                "Issue": "Dataset is empty or could not be loaded",
                "Count": 1,
            })
            continue

        missing_count = int(df.isna().sum().sum())
        duplicate_count = int(df.duplicated().sum())

        if missing_count:
            flags.append({
                "Dataset": dataset_name,
                "Issue": "Missing values",
                "Count": missing_count,
            })

        if duplicate_count:
            flags.append({
                "Dataset": dataset_name,
                "Issue": "Duplicate rows",
                "Count": duplicate_count,
            })

    if not video_data.empty and "views" in video_data.columns:
        views = pd.to_numeric(video_data["views"], errors="coerce")
        zero_views = int((views.fillna(0) <= 0).sum())

        if zero_views:
            flags.append({
                "Dataset": "video_data",
                "Issue": "Zero or negative views",
                "Count": zero_views,
            })

    if not flags:
        st.success("No basic performance or data-quality flags detected.")
    else:
        flags_df = pd.DataFrame(flags)
        st.metric("Flag Types", len(flags_df))
        show_table(flags_df)

    st.caption(
        "These are basic automated checks. A flag indicates something "
        "to review, not necessarily an error or poor creator performance."
    )


# ============================================================
# 12. DATA QUALITY
# ============================================================

elif page == "Data Quality":
    hero(
        "Data Quality",
        "Review file availability, schema, missing values and duplicate rows.",
    )

    if load_errors:
        st.warning("Some data files could not be loaded:")
        for error in load_errors:
            st.write(f"- {error}")
    else:
        st.success("All configured CSV files were loaded.")

    quality_rows = []

    for name, df in data.items():
        filepath = DATA_PATH / DATA_FILES[name]

        quality_rows.append({
            "Dataset": name,
            "File": DATA_FILES[name],
            "Exists": filepath.exists(),
            "Rows": len(df),
            "Columns": len(df.columns),
            "Missing Values": int(df.isna().sum().sum())
            if not df.empty else 0,
            "Duplicate Rows": int(df.duplicated().sum())
            if not df.empty else 0,
        })

    quality_df = pd.DataFrame(quality_rows)
    show_table(quality_df)

    st.divider()
    section_title("Dataset Schema")

    dataset_choice = st.selectbox(
        "Choose a dataset",
        list(data.keys()),
    )
    selected_df = data[dataset_choice]

    if selected_df.empty:
        st.warning("This dataset is empty or unavailable.")
    else:
        schema_df = pd.DataFrame({
            "Column": selected_df.columns,
            "Data Type": [
                str(dtype) for dtype in selected_df.dtypes
            ],
            "Missing Values": [
                int(selected_df[col].isna().sum())
                for col in selected_df.columns
            ],
            "Unique Values": [
                int(selected_df[col].nunique(dropna=True))
                for col in selected_df.columns
            ],
        })

        show_table(schema_df)

        if "validate_dataframe" in globals():
            try:
                issues = validate_dataframe(
                    selected_df,
                    dataset_choice,
                )

                section_title("Validation Results")

                if issues:
                    for issue in issues:
                        st.warning(str(issue))
                else:
                    st.success("No basic validation issues detected.")
            except Exception as exc:
                st.info(f"Validation helper could not run: {exc}")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "CreatorBridge | Creator Marketing Intelligence | "
    "Use the available source data to support decisions."
)
