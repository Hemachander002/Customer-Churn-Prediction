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

.stDataFrame {
    border-radius: 10px;
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

st.sidebar.info(
    """
    Upload customer data to:
    
    • Predict customer churn
    
    • Identify high-risk customers
    
    • Generate analytics
    
    • Export executive reports
    """
)


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
    revenue_risk
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 18)

    pdf.cell(
        200,
        10,
        txt="Customer Churn Analytics Report",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    pdf.cell(
        200,
        10,
        txt=f"Generated on: {datetime.now()}",
        ln=True
    )

    pdf.ln(5)

    pdf.multi_cell(
        0,
        10,
        txt=f"""
Total Customers: {total_customers}

Predicted Churn Rate: {churn_rate:.2f}%

High Risk Customers: {high_risk_customers}

Average Churn Probability: {avg_probability:.2f}%

Revenue At Risk: ${revenue_risk:,.2f}
"""
    )

    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)

    pdf.cell(
        200,
        10,
        txt="Executive Insights",
        ln=True
    )

    pdf.set_font("Arial", size=12)

    pdf.multi_cell(
        0,
        10,
        txt=f"""
• {high_risk_customers} customers are classified as high churn risk.

• Retention campaigns should focus on high-risk customers.

• Customers with high monthly charges show increased churn probability.

• Churn prevention strategies can significantly reduce revenue loss.
"""
    )

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

    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Dataset Preview
    with st.expander("Preview Uploaded Dataset"):

        st.dataframe(df.head())

    # Run Predictions
    result_df = pipeline.predict(df)

    st.success(
        "Churn analytics generated successfully!"
    )

    # =====================================================
    # SIDEBAR FILTERS
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
    # KPI METRICS
    # =====================================================

    total_customers = len(result_df)

    high_risk_customers = len(
        result_df[result_df["risk_level"] == "High Risk"]
    )

    churn_rate = (
        result_df["prediction"].mean() * 100
    )

    avg_probability = (
        result_df["churn_probability"].mean() * 100
    )

    revenue_risk = 0

    if "monthlycharges" in result_df.columns:

        revenue_risk = result_df[
            result_df["prediction"] == 1
        ]["monthlycharges"].sum()

    # =====================================================
    # KPI SECTION
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
    # TAB 1 — ANALYTICS
    # =====================================================

    with tab1:

        st.subheader("Customer Churn Distribution")

        fig = px.pie(
            result_df,
            names="prediction_label",
            hole=0.45,
            title="Churn vs Non-Churn Customers"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Risk Segmentation

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

        # Probability Distribution

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

        # Contract Analysis

        if "contract" in result_df.columns:

            contract_chart = px.histogram(
                result_df,
                x="contract",
                color="prediction_label",
                barmode="group",
                title="Contract Type vs Churn"
            )

            contract_chart.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                contract_chart,
                use_container_width=True
            )

        # Top Risk Customers

        st.subheader("Top High-Risk Customers")

        top_risk = result_df.sort_values(
            by="churn_probability",
            ascending=False
        ).head(10)

        st.dataframe(top_risk)

    # =====================================================
    # TAB 2 — RESULTS
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

        # CSV Download

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Churn Report CSV",
            data=csv,
            file_name="customer_churn_report.csv",
            mime="text/csv"
        )

    # =====================================================
    # TAB 3 — INSIGHTS
    # =====================================================

    with tab3:

        st.subheader("Executive Business Insights")

        high_risk_pct = (
            high_risk_customers / total_customers
        ) * 100

        st.info(f"""
• {high_risk_pct:.1f}% customers are classified as high churn risk.

• Average churn probability across all customers is {avg_probability:.2f}%.

• Customers with month-to-month contracts appear more vulnerable to churn.

• High monthly charges correlate strongly with churn likelihood.

• Retention campaigns should prioritize high-risk customers immediately.

• Estimated revenue at risk is ${revenue_risk:,.2f}.
""")

        # PDF Export

        if st.button("Generate PDF Report"):

            generate_pdf(
                total_customers,
                churn_rate,
                high_risk_customers,
                avg_probability,
                revenue_risk
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


### second best one

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt

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

.stDataFrame {
    border-radius: 10px;
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

st.sidebar.info(
    """
    Upload customer data to:
    
    • Predict customer churn
    
    • Identify high-risk customers
    
    • Generate analytics
    
    • Export executive reports
    """
)


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
    revenue_risk
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 18)

    pdf.cell(
        200,
        10,
        txt="Customer Churn Analytics Report",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    pdf.cell(
        200,
        10,
        txt=f"Generated on: {datetime.now()}",
        ln=True
    )

    pdf.ln(5)

    pdf.multi_cell(
        0,
        10,
        txt=f"""
Total Customers: {total_customers}

Predicted Churn Rate: {churn_rate:.2f}%

High Risk Customers: {high_risk_customers}

Average Churn Probability: {avg_probability:.2f}%

Revenue At Risk: ${revenue_risk:,.2f}
"""
    )

    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)

    pdf.cell(
        200,
        10,
        txt="Executive Insights",
        ln=True
    )

    pdf.set_font("Arial", size=12)

    pdf.multi_cell(
        0,
        10,
        txt=f"""
• {high_risk_customers} customers are classified as high churn risk.

• Retention campaigns should focus on high-risk customers.

• Customers with high monthly charges show increased churn probability.

• Churn prevention strategies can significantly reduce revenue loss.
"""
    )

    # =====================================================
    # ADD CHARTS TO PDF
    # =====================================================

    pdf.add_page()

    pdf.set_font("Arial", "B", 16)

    pdf.cell(
        200,
        10,
        txt="Visual Analytics",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.image(
        "gender_chart.png",
        x=10,
        w=180
    )

    pdf.ln(10)

    pdf.image(
        "senior_chart.png",
        x=10,
        w=180
    )

    pdf.ln(10)

    pdf.image(
        "backup_chart.png",
        x=10,
        w=180
    )

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

    # -------------------------------------------------
    # READ CSV
    # -------------------------------------------------

    df = pd.read_csv(uploaded_file)

    # -------------------------------------------------
    # PREVIEW DATASET
    # -------------------------------------------------

    with st.expander("Preview Uploaded Dataset"):

        st.dataframe(df.head())

    # -------------------------------------------------
    # RUN PREDICTIONS
    # -------------------------------------------------

    result_df = pipeline.predict(df)

    st.success(
        "Churn analytics generated successfully!"
    )

    # =====================================================
    # SIDEBAR FILTERS
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
    # KPI METRICS
    # =====================================================

    total_customers = len(result_df)

    high_risk_customers = len(
        result_df[result_df["risk_level"] == "High Risk"]
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
    # KPI SECTION
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
    # TAB 1 — ANALYTICS
    # =====================================================

    with tab1:

        # -------------------------------------------------
        # PIE CHART
        # -------------------------------------------------

        st.subheader("Customer Churn Distribution")

        fig = px.pie(
            result_df,
            names="prediction_label",
            hole=0.45,
            title="Churn vs Non-Churn Customers"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -------------------------------------------------
        # RISK SEGMENTATION
        # -------------------------------------------------

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

        # -------------------------------------------------
        # GENDER CHURN ANALYSIS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SENIOR CITIZEN ANALYSIS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ONLINE BACKUP ANALYSIS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SAVE CHARTS FOR PDF
        # -------------------------------------------------

        gender_chart.write_image("gender_chart.png")

        senior_chart.write_image("senior_chart.png")

        backup_chart.write_image("backup_chart.png")

        # -------------------------------------------------
        # TOP HIGH RISK CUSTOMERS
        # -------------------------------------------------

        st.subheader("Top High-Risk Customers")

        top_risk = result_df.sort_values(
            by="churn_probability",
            ascending=False
        ).head(10)

        st.dataframe(top_risk)

    # =====================================================
    # TAB 2 — RESULTS
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

        # CSV Download

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Churn Report CSV",
            data=csv,
            file_name="customer_churn_report.csv",
            mime="text/csv"
        )

    # =====================================================
    # TAB 3 — INSIGHTS
    # =====================================================

    with tab3:

        st.subheader("Executive Business Insights")

        high_risk_pct = (
            high_risk_customers / total_customers
        ) * 100

        st.info(f"""
• {high_risk_pct:.1f}% customers are classified as high churn risk.

• Average churn probability across all customers is {avg_probability:.2f}%.

• Customers with month-to-month contracts appear more vulnerable to churn.

• High monthly charges correlate strongly with churn likelihood.

• Senior citizens demonstrate elevated churn behavior.

• Customers without online backup services show increased churn risk.

• Retention campaigns should prioritize high-risk customers immediately.

• Estimated revenue at risk is ${revenue_risk:,.2f}.
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
                revenue_risk
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