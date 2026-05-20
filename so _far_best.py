import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

from src.customer_churn_prediction.pipeline.preprocessing_pipeline import PredictionPipeline


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Customer Churn Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

[data-testid="stMetric"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HERO SECTION
# =====================================================

st.markdown("""
<div style="
    background: linear-gradient(
        90deg,
        #141E30,
        #243B55
    );
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
">

<h1 style="
    color:white;
    text-align:center;
    font-size:42px;
">
AI-Powered Customer Churn Analytics Platform
</h1>

<p style="
    color:#D3D3D3;
    text-align:center;
    font-size:18px;
">
Upload customer datasets, predict churn risk,
generate business insights, and export executive reports.
</p>

</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Dashboard Controls")

st.sidebar.markdown("---")

st.sidebar.success("Prediction Pipeline Active")

st.sidebar.info("""
Upload customer data to:

• Predict customer churn
• Identify high-risk customers
• Generate analytics
• Export executive reports
""")

# =====================================================
# LOAD PIPELINE
# =====================================================

pipeline = PredictionPipeline()

# =====================================================
# PDF GENERATOR
# =====================================================

def generate_pdf(
    total_customers,
    churn_rate,
    high_risk_customers,
    avg_probability,
    revenue_risk,
    result_df
):

    pdf = FPDF()

    pdf.set_auto_page_break(auto=True, margin=15)

    # =====================================================
    # PAGE 1
    # =====================================================

    pdf.add_page()

    pdf.set_font("Arial", "B", 20)

    pdf.cell(
        200,
        10,
        txt="Customer Churn Analytics Report",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font("Arial", "", 12)

    pdf.cell(
        200,
        10,
        txt=f"Generated on: {datetime.now()}",
        ln=True
    )

    pdf.ln(10)

    # =====================================================
    # KPI SECTION
    # =====================================================

    pdf.set_font("Arial", "B", 14)

    pdf.cell(200, 10, txt="Business KPIs", ln=True)

    pdf.set_font("Arial", "", 12)

    kpi_text = f"""
Total Customers: {total_customers}

Predicted Churn Rate: {churn_rate:.2f}%

High Risk Customers: {high_risk_customers}

Average Churn Probability: {avg_probability:.2f}%

Revenue At Risk: ${revenue_risk:,.2f}
"""

    pdf.multi_cell(0, 10, txt=kpi_text)

    # =====================================================
    # EXECUTIVE INSIGHTS
    # =====================================================

    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)

    pdf.cell(200, 10, txt="Executive Insights", ln=True)

    pdf.set_font("Arial", "", 12)

    insights = f"""
- {high_risk_customers} customers are classified as high churn risk.

- Customers with month-to-month contracts show higher churn probability.

- High monthly charge customers demonstrate increased churn behavior.

- Senior citizens appear more likely to churn.

- Customers without online backup services show higher churn risk.

- Retention campaigns should prioritize high-risk customers immediately.

- Estimated revenue at risk is ${revenue_risk:,.2f}.
"""

    pdf.multi_cell(0, 10, txt=insights)

    # =====================================================
    # PAGE 2 — VISUAL ANALYTICS
    # =====================================================

    pdf.add_page()

    pdf.set_font("Arial", "B", 18)

    pdf.cell(
        200,
        10,
        txt="Visual Analytics",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    chart_files = [
        "churn_distribution.png",
        "gender_chart.png",
        "senior_chart.png",
        "backup_chart.png",
        "risk_chart.png",
        "probability_chart.png"
    ]

    for chart in chart_files:

        pdf.image(chart, x=10, w=180)

        pdf.ln(10)

    # =====================================================
    # PAGE 3 — TOP HIGH RISK CUSTOMERS
    # =====================================================

    pdf.add_page()

    pdf.set_font("Arial", "B", 16)

    pdf.cell(
        200,
        10,
        txt="Top High-Risk Customers",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    top_risk = result_df.sort_values(
        by="churn_probability",
        ascending=False
    ).head(10)

    pdf.set_font("Arial", "B", 10)

    pdf.cell(60, 10, "Customer", 1)
    pdf.cell(40, 10, "Risk Level", 1)
    pdf.cell(40, 10, "Probability", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)

    for _, row in top_risk.iterrows():

        customer = str(row.get("customerID", "N/A"))

        risk = str(row["risk_level"])

        prob = f"{row['churn_probability']:.2f}"

        pdf.cell(60, 10, customer, 1)
        pdf.cell(40, 10, risk, 1)
        pdf.cell(40, 10, prob, 1)

        pdf.ln()

    pdf.output("customer_churn_report.pdf")


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Customer CSV File",
    type=["csv"]
)

# =====================================================
# PROCESS FILE
# =====================================================

if uploaded_file is not None:

    # =====================================================
    # READ DATA
    # =====================================================

    df = pd.read_csv(uploaded_file)

    with st.expander("Preview Uploaded Dataset"):

        st.dataframe(df.head())

    # =====================================================
    # PREDICTIONS
    # =====================================================

    result_df = pipeline.predict(df)

    st.success(
        "Churn analytics generated successfully!"
    )

    # =====================================================
    # FILTERS
    # =====================================================

    risk_filter = st.sidebar.multiselect(
        "Filter Risk Levels",
        options=result_df["risk_level"].unique(),
        default=result_df["risk_level"].unique()
    )

    result_df = result_df[
        result_df["risk_level"].isin(risk_filter)
    ]

    # =====================================================
    # KPIs
    # =====================================================

    total_customers = len(result_df)

    high_risk_customers = len(
        result_df[
            result_df["risk_level"] == "High Risk"
        ]
    )

    churn_rate = (
        result_df["prediction"].mean() * 100
    )

    avg_probability = (
        result_df["churn_probability"].mean() * 100
    )

    revenue_risk = 0

    if "MonthlyCharges" in result_df.columns:

        revenue_risk = result_df[
            result_df["prediction"] == 1
        ]["MonthlyCharges"].sum()

    # =====================================================
    # KPI CARDS
    # =====================================================

    st.markdown("## Business KPIs")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Customers",
        total_customers
    )

    col2.metric(
        "Predicted Churn Rate",
        f"{churn_rate:.2f}%"
    )

    col3.metric(
        "High Risk Customers",
        high_risk_customers
    )

    col4.metric(
        "Avg Churn Probability",
        f"{avg_probability:.2f}%"
    )

    col5.metric(
        "Revenue At Risk",
        f"${revenue_risk:,.2f}"
    )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs([
        "Analytics Dashboard",
        "Prediction Results",
        "Executive Insights"
    ])

    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        # =====================================================
        # CHURN DISTRIBUTION
        # =====================================================

        st.subheader("Customer Churn Distribution")

        fig = px.pie(
            result_df,
            names="prediction_label",
            hole=0.45,
            title="Churn Distribution"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        fig.write_image("churn_distribution.png")

        # =====================================================
        # RISK SEGMENTATION
        # =====================================================

        risk_chart = px.histogram(
            result_df,
            x="risk_level",
            color="risk_level",
            title="Customer Risk Segmentation"
        )

        risk_chart.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            risk_chart,
            use_container_width=True
        )

        risk_chart.write_image("risk_chart.png")

        # =====================================================
        # PROBABILITY DISTRIBUTION
        # =====================================================

        prob_chart = px.histogram(
            result_df,
            x="churn_probability",
            nbins=30,
            title="Churn Probability Distribution"
        )

        prob_chart.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            prob_chart,
            use_container_width=True
        )

        prob_chart.write_image(
            "probability_chart.png"
        )

        # =====================================================
        # GENDER ANALYSIS
        # =====================================================

        st.subheader("Gender vs Churn")

        gender_chart = px.histogram(
            result_df,
            x="gender",
            color="prediction_label",
            barmode="group",
            title="Gender-wise Churn Distribution"
        )

        gender_chart.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            gender_chart,
            use_container_width=True
        )

        gender_chart.write_image(
            "gender_chart.png"
        )

        # =====================================================
        # SENIOR CITIZEN ANALYSIS
        # =====================================================

        st.subheader("Senior Citizen Churn Analysis")

        senior_chart = px.histogram(
            result_df,
            x="SeniorCitizen",
            color="prediction_label",
            barmode="group",
            title="Senior Citizen vs Churn"
        )

        senior_chart.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            senior_chart,
            use_container_width=True
        )

        senior_chart.write_image(
            "senior_chart.png"
        )

        # =====================================================
        # ONLINE BACKUP ANALYSIS
        # =====================================================

        st.subheader("Online Backup vs Churn")

        backup_chart = px.histogram(
            result_df,
            x="OnlineBackup",
            color="prediction_label",
            barmode="group",
            title="Online Backup Service vs Churn"
        )

        backup_chart.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            backup_chart,
            use_container_width=True
        )

        backup_chart.write_image(
            "backup_chart.png"
        )

        # =====================================================
        # TOP HIGH-RISK CUSTOMERS
        # =====================================================

        st.subheader("Top High-Risk Customers")

        top_risk = result_df.sort_values(
            by="churn_probability",
            ascending=False
        ).head(10)

        st.dataframe(top_risk)

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        st.subheader("Prediction Results")

        search = st.text_input(
            "Search Customers"
        )

        filtered_df = result_df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df.astype(str)
                .apply(
                    lambda row: row.str.contains(
                        search,
                        case=False
                    ).any(),
                    axis=1
                )
            ]

        st.dataframe(filtered_df)

        # =====================================================
        # CSV DOWNLOAD
        # =====================================================

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Churn Report CSV",
            data=csv,
            file_name="customer_churn_report.csv",
            mime="text/csv"
        )

    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        st.subheader("Executive Business Insights")

        high_risk_pct = (
            high_risk_customers / total_customers
        ) * 100

        st.info(f"""
- {high_risk_pct:.1f}% customers are classified as high churn risk.

- Customers with month-to-month contracts appear more vulnerable to churn.

- Senior citizens demonstrate elevated churn behavior.

- Customers without online backup services show increased churn risk.

- High monthly charges correlate strongly with churn likelihood.

- Estimated revenue at risk is ${revenue_risk:,.2f}.
""")

        # =====================================================
        # PDF EXPORT
        # =====================================================

        if st.button("Generate PDF Report"):

            generate_pdf(
                total_customers,
                churn_rate,
                high_risk_customers,
                avg_probability,
                revenue_risk,
                result_df
            )

            with open(
                "customer_churn_report.pdf",
                "rb"
            ) as file:

                st.download_button(
                    label="Download PDF Report",
                    data=file,
                    file_name="customer_churn_report.pdf",
                    mime="application/pdf"
                )

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<hr>

<center>
AI-Powered Customer Churn Analytics Platform
</center>
""", unsafe_allow_html=True)