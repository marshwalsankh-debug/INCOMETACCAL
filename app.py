import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tax Calculator", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Functions ----------
def calculate_tax(income):
    slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float("inf"), 0.30),
    ]

    prev_limit = 0
    tax = 0
    breakdown = []

    for limit, rate in slabs:
        if income > prev_limit:
            taxable = min(income, limit) - prev_limit
            slab_tax = taxable * rate
            tax += slab_tax

            breakdown.append({
                "Slab": f"{prev_limit}-{limit}",
                "Tax": slab_tax
            })

            prev_limit = limit
        else:
            break

    return tax, breakdown


def calculate_surcharge(income, tax):
    if income > 50000000:
        return tax * 0.37
    elif income > 20000000:
        return tax * 0.25
    elif income > 10000000:
        return tax * 0.15
    elif income > 5000000:
        return tax * 0.10
    return 0


# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Settings")

    income = st.slider(
        "Annual Income (₹)",
        0, 5000000, 800000, step=50000
    )

    st.markdown("---")
    st.caption("New Tax Regime\nIncludes surcharge + 4% cess")

# ---------- Header ----------
st.title("💰 Income Tax Calculator")
st.caption("New Regime | Clean Breakdown | Visual Insights")

# ---------- Calculation ----------
base_tax, breakdown = calculate_tax(income)
surcharge = calculate_surcharge(income, base_tax)
cess = (base_tax + surcharge) * 0.04
total_tax = base_tax + surcharge + cess

effective_rate = (total_tax / income * 100) if income > 0 else 0

# ---------- Metrics (Top Cards) ----------
col1, col2, col3 = st.columns(3)

col1.metric("Total Tax", f"₹{total_tax:,.0f}")
col2.metric("Effective Rate", f"{effective_rate:.2f}%")
col3.metric("Cess + Surcharge", f"₹{(cess+surcharge):,.0f}")

# ---------- Prepare Data ----------
df = pd.DataFrame(breakdown)

def format_slab(s):
    start, end = s.split("-")
    return f"₹{int(float(start))/100000:.0f}L - ₹{int(float(end))/100000:.0f}L"

df["Slab"] = [f"{i}" for i in [b["Slab"] for b in breakdown]]
df["Slab"] = df["Slab"].str.replace("inf", "1000000000")
df["Slab"] = df["Slab"].apply(format_slab)

# ---------- Layout ----------
left, right = st.columns([1, 1])

# Table
with left:
    st.subheader("📊 Tax Breakdown")
    st.dataframe(df, use_container_width=True)

# Chart
with right:
    st.subheader("📈 Tax Distribution")

    fig = px.bar(
        df,
        x="Tax",
        y="Slab",
        orientation="h",
        text="Tax",
        color="Tax",
        color_continuous_scale="teal"
    )

    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
st.markdown("---")
st.subheader("📩 Get a Detailed Tax Report")

st.write("Enter your details to receive a personalized tax report and saving tips.")

with st.form("lead_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")

    submitted = st.form_submit_button("Get Report")

    if submitted:
        if name and email:
            # Save to CSV
            lead_data = pd.DataFrame([{
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Income": income,
                "Tax": total_tax
            }])

            try:
                lead_data.to_csv("leads.csv", mode='a', header=False, index=False)
            except:
                lead_data.to_csv("leads.csv", index=False)

            st.success("✅ रिपोर्ट भेज दी जाएगी! (We'll contact you soon)")
        else:
            st.error("Please fill in required fields (Name & Email)")