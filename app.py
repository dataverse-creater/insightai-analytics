import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="InsightAI | Data Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #15132d);
    color: #f5f5ff;
}
[data-testid="stSidebar"] {
    background: #0c1021;
    border-right: 1px solid #302d50;
}
h1, h2, h3 { color: #f5f3ff !important; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #191f3b, #282044);
    border: 1px solid #403765;
    border-radius: 14px;
    padding: 16px;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, #6d5dfc, #a855f7);
    color: white;
    border: none;
    border-radius: 9px;
}
.insight-header {
    background: linear-gradient(110deg, #211c49, #172544, #292052);
    border: 1px solid #39366a;
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 22px;
}
.insight-header p { color: #c9c9ed; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("# ◈ InsightAI")
st.sidebar.caption("DATA ANALYTICS WORKSPACE")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    ["Overview", "Analytics Studio", "Data Quality", "Ask Your Data"]
)

st.sidebar.divider()
st.sidebar.markdown("### Upload Dataset")

files = st.sidebar.file_uploader(
    "Upload CSV file(s)",
    type=["csv"],
    accept_multiple_files=True
)

# ---------------- LOAD DATA ----------------
datasets = {}

if files:
    for file in files:
        try:
            file.seek(0)
            try:
                data = pd.read_csv(file, encoding="utf-8")
            except UnicodeDecodeError:
                file.seek(0)
                data = pd.read_csv(file, encoding="latin-1")

            if not data.empty:
                datasets[file.name] = data
            else:
                st.sidebar.warning(f"{file.name} is empty.")
        except Exception as error:
            st.sidebar.error(f"Cannot read {file.name}: {error}")

if datasets:
    selected_file = st.sidebar.selectbox(
        "Select active dataset",
        list(datasets.keys())
    )
    df = datasets[selected_file].copy()
else:
    selected_file = None
    df = None

# ---------------- HEADER ----------------
st.markdown("""
<div class="insight-header">
    <h1>InsightAI</h1>
    <p>Your data. Clear insights. Better decisions.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- EMPTY STATE ----------------
if df is None:
    st.title("Welcome to your analytics workspace")
    st.write("Upload a CSV file from the sidebar to get started.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("01 · Explore")
        st.write("Preview data and understand dataset structure.")

    with c2:
        st.subheader("02 · Analyze")
        st.write("Create interactive charts and view statistics.")

    with c3:
        st.subheader("03 · Improve")
        st.write("Identify missing values and duplicate records.")

    st.stop()

# ---------------- COMMON DATA ----------------
rows, cols = df.shape
numeric_cols = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

# ---------------- OVERVIEW ----------------
if page == "Overview":

    st.subheader("Dataset Overview")
    st.caption(f"Active dataset: {selected_file}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Rows", f"{rows:,}")
    c2.metric("Total Columns", f"{cols:,}")
    c3.metric("Missing Cells", f"{int(df.isna().sum().sum()):,}")
    c4.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")

    st.markdown("### Data Preview")
    st.dataframe(df.head(100), use_container_width=True, hide_index=True)

    left, right = st.columns(2)

    with left:
        st.markdown("### Column Information")

        column_info = pd.DataFrame({
            "Column": df.columns.astype(str),
            "Data Type": [str(x) for x in df.dtypes],
            "Missing Values": [
                int(df[column].isna().sum()) for column in df.columns
            ]
        })

        st.dataframe(
            column_info,
            use_container_width=True,
            hide_index=True
        )

    with right:
        st.markdown("### Statistical Summary")

        if numeric_cols:
            st.dataframe(
                df[numeric_cols].describe().T.round(2),
                use_container_width=True
            )
        else:
            st.info("No numeric columns are available.")

    st.download_button(
        "Download Dataset CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="insightai_dataset.csv",
        mime="text/csv"
    )

# ---------------- ANALYTICS STUDIO ----------------
elif page == "Analytics Studio":

    st.subheader("Analytics Studio")
    st.write("Build interactive visualizations from your dataset.")

    chart_type = st.selectbox(
        "Choose visualization",
        ["Histogram", "Bar Chart", "Line Chart", "Scatter Plot", "Box Plot"]
    )

    fig = None

    if chart_type == "Histogram":

        if numeric_cols:
            column = st.selectbox("Select numeric column", numeric_cols)
            bins = st.slider("Number of bins", 5, 60, 20)

            fig = px.histogram(
                df,
                x=column,
                nbins=bins,
                title=f"Distribution of {column}",
                template="plotly_dark",
                color_discrete_sequence=["#8b5cf6"]
            )
        else:
            st.warning("This chart requires a numeric column.")

    elif chart_type == "Bar Chart":

        if category_cols:
            x_col = st.selectbox("Category column", category_cols)

            if numeric_cols:
                y_col = st.selectbox("Value column", numeric_cols)
                aggregation = st.selectbox(
                    "Aggregation",
                    ["sum", "mean", "count"]
                )

                grouped = df.groupby(
                    x_col, dropna=False
                )[y_col].agg(aggregation).reset_index()

                grouped[x_col] = grouped[x_col].astype(str)

                fig = px.bar(
                    grouped,
                    x=x_col,
                    y=y_col,
                    title=f"{aggregation.title()} of {y_col} by {x_col}",
                    template="plotly_dark",
                    color_discrete_sequence=["#8b5cf6"]
                )
            else:
                counts = (
                    df[x_col].astype(str)
                    .value_counts()
                    .head(30)
                    .rename_axis(x_col)
                    .reset_index(name="Count")
                )

                fig = px.bar(
                    counts,
                    x=x_col,
                    y="Count",
                    title=f"Count by {x_col}",
                    template="plotly_dark",
                    color_discrete_sequence=["#8b5cf6"]
                )
        else:
            st.warning("This chart requires a category column.")

    elif chart_type == "Line Chart":

        if numeric_cols:
            x_col = st.selectbox("X-axis", list(df.columns))
            y_col = st.selectbox("Y-axis", numeric_cols)

            chart_data = df[[x_col, y_col]].dropna()

            fig = px.line(
                chart_data,
                x=x_col,
                y=y_col,
                markers=True,
                title=f"{y_col} across {x_col}",
                template="plotly_dark"
            )
        else:
            st.warning("This chart requires a numeric column.")

    elif chart_type == "Scatter Plot":

        if len(numeric_cols) >= 2:
            x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
            y_options = [c for c in numeric_cols if c != x_col]
            y_col = st.selectbox("Y-axis", y_options, key="scatter_y")

            color_options = ["None"] + category_cols
            color_col = st.selectbox("Color by", color_options)

            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=None if color_col == "None" else color_col,
                title=f"{y_col} vs {x_col}",
                template="plotly_dark"
            )
        else:
            st.warning("Scatter plot requires at least two numeric columns.")

    elif chart_type == "Box Plot":

        if numeric_cols:
            y_col = st.selectbox("Numeric column", numeric_cols)
            group_options = ["None"] + category_cols
            group_col = st.selectbox("Group by", group_options)

            fig = px.box(
                df,
                x=None if group_col == "None" else group_col,
                y=y_col,
                title=f"Distribution of {y_col}",
                template="plotly_dark"
            )
        else:
            st.warning("This chart requires a numeric column.")

    if fig is not None:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#eeeeff"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Quick Statistics")

    if numeric_cols:
        metric_col = st.selectbox(
            "Select numeric column",
            numeric_cols,
            key="stats_column"
        )

        series = df[metric_col]
        a, b, c, d = st.columns(4)

        a.metric("Average", f"{series.mean():,.2f}")
        b.metric("Median", f"{series.median():,.2f}")
        c.metric("Minimum", f"{series.min():,.2f}")
        d.metric("Maximum", f"{series.max():,.2f}")
    else:
        st.info("No numeric columns available for statistics.")

# ---------------- DATA QUALITY ----------------
elif page == "Data Quality":

    st.subheader("Data Quality Report")
    st.write("Review missing values, duplicates, and column completeness.")

    missing_total = int(df.isna().sum().sum())
    duplicate_total = int(df.duplicated().sum())
    total_cells = max(rows * cols, 1)
    missing_percent = missing_total / total_cells * 100

    a, b, c = st.columns(3)

    a.metric("Missing Cells", f"{missing_total:,}",
             f"{missing_percent:.2f}% of all cells")
    b.metric("Duplicate Rows", f"{duplicate_total:,}")
    c.metric("Complete Rows", f"{int((~df.isna().any(axis=1)).sum()):,}")

    quality = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": [str(df[col].dtype) for col in df.columns],
        "Missing Values": [int(df[col].isna().sum()) for col in df.columns],
        "Missing %": [
            round(float(df[col].isna().mean() * 100), 2)
            for col in df.columns
        ],
        "Unique Values": [int(df[col].nunique()) for col in df.columns]
    })

    st.markdown("### Column-level Report")
    st.dataframe(quality, use_container_width=True, hide_index=True)

    if missing_total > 0:
        missing_data = quality[quality["Missing Values"] > 0]

        fig = px.bar(
            missing_data,
            x="Column",
            y="Missing Values",
            title="Missing Values by Column",
            template="plotly_dark",
            color_discrete_sequence=["#a855f7"]
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing values found.")

    st.markdown("### Clean Dataset")

    remove_duplicates = st.checkbox("Remove duplicate rows")
    remove_missing = st.checkbox("Remove rows containing missing values")

    cleaned_df = df.copy()

    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates()

    if remove_missing:
        cleaned_df = cleaned_df.dropna()

    st.caption(
        f"Cleaned dataset: {len(cleaned_df):,} rows × "
        f"{len(cleaned_df.columns):,} columns"
    )

    st.download_button(
        "Download Cleaned CSV",
        data=cleaned_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="insightai_cleaned_data.csv",
        mime="text/csv"
    )

# ---------------- ASK YOUR DATA ----------------
elif page == "Ask Your Data":

    st.subheader("Ask Your Data")
    st.write("Ask basic questions about your uploaded dataset.")

    st.info(
        "This version uses rule-based analysis. "
        "It does not yet connect to an external AI model."
    )

    question = st.text_input(
        "Enter your question",
        placeholder="Example: How many rows are in the dataset?"
    )

    if st.button("Analyze Question"):

        q = question.lower().strip()

        if not q:
            st.warning("Please enter a question.")

        elif any(x in q for x in [
            "how many rows", "row count", "number of rows", "total rows"
        ]):
            st.success(f"The dataset contains {rows:,} rows.")

        elif any(x in q for x in [
            "how many columns", "column count",
            "number of columns", "total columns"
        ]):
            st.success(f"The dataset contains {cols:,} columns.")

        elif "duplicate" in q:
            st.success(
                f"Found {int(df.duplicated().sum()):,} duplicate rows."
            )

        elif any(x in q for x in ["missing", "null", "empty values"]):
            missing = df.isna().sum()
            missing = missing[missing > 0].sort_values(ascending=False)

            if missing.empty:
                st.success("No missing values were found.")
            else:
                result = missing.rename_axis("Column").reset_index(
                    name="Missing Values"
                )
                st.dataframe(result, use_container_width=True, hide_index=True)

        elif "column" in q or "fields" in q:
            st.success("Columns: " + ", ".join(map(str, df.columns)))

        elif any(x in q for x in [
            "average", "mean", "median", "maximum",
            "minimum", "max", "min", "sum", "total"
        ]):

            matched = [
                col for col in numeric_cols
                if str(col).lower() in q
            ]

            if not matched:
                st.write("Available numeric columns:")
                st.write(", ".join(map(str, numeric_cols)))
                st.caption(
                    "Include a column name in your question, "
                    "such as: What is the average Sales?"
                )
            else:
                col = matched[0]

                if "median" in q:
                    result = df[col].median()
                    label = "Median"
                elif "maximum" in q or "max" in q:
                    result = df[col].max()
                    label = "Maximum"
                elif "minimum" in q or "min" in q:
                    result = df[col].min()
                    label = "Minimum"
                elif "sum" in q or "total" in q:
                    result = df[col].sum()
                    label = "Sum"
                else:
                    result = df[col].mean()
                    label = "Average"

                st.success(f"{label} of {col}: {result:,.2f}")

        else:
            st.warning(
                "Try asking about row count, column names, missing values, "
                "duplicates, or the average, median, sum, minimum, "
                "or maximum of a numeric column."
            )

    st.markdown("### Suggested Questions")
    st.markdown("""
    - How many rows are in the dataset?
    - Which columns have missing values?
    - How many duplicate rows are there?
    - What is the average of Sales?
    """)

# ---------------- FOOTER ----------------
st.divider()
st.caption("InsightAI · Interactive Data Analytics Workspace")