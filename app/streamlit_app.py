# -------------------------
# ROI, Reach & Conversion Estimates
# -------------------------
st.subheader("📈 ROI, Reach & Conversion Estimates")

# Simple example assumptions per goal & platform
# CPM = cost per 1,000 impressions
DEFAULT_ASSUMPTIONS = {
    "awareness": {
        "meta":   {"cpm": 6,  "ctr": 0.008, "conv_rate": 0.003},
        "google": {"cpm": 10, "ctr": 0.02,  "conv_rate": 0.01},
        "tiktok": {"cpm": 4,  "ctr": 0.015, "conv_rate": 0.004},
        "x":      {"cpm": 5,  "ctr": 0.01,  "conv_rate": 0.003},
    },
    "traffic": {
        "meta":   {"cpm": 7,  "ctr": 0.015, "conv_rate": 0.008},
        "google": {"cpm": 12, "ctr": 0.03,  "conv_rate": 0.012},
        "tiktok": {"cpm": 5,  "ctr": 0.02,  "conv_rate": 0.007},
        "x":      {"cpm": 6,  "ctr": 0.015, "conv_rate": 0.005},
    },
    "leads": {
        "meta":   {"cpm": 8,  "ctr": 0.018, "conv_rate": 0.03},
        "google": {"cpm": 14, "ctr": 0.035, "conv_rate": 0.06},
        "tiktok": {"cpm": 6,  "ctr": 0.02,  "conv_rate": 0.025},
        "x":      {"cpm": 7,  "ctr": 0.015, "conv_rate": 0.02},
    },
    "conversions": {
        "meta":   {"cpm": 9,  "ctr": 0.02,  "conv_rate": 0.04},
        "google": {"cpm": 15, "ctr": 0.04,  "conv_rate": 0.07},
        "tiktok": {"cpm": 7,  "ctr": 0.022, "conv_rate": 0.03},
        "x":      {"cpm": 8,  "ctr": 0.018, "conv_rate": 0.025},
    },
    "sales": {  # treat similar to conversions
        "meta":   {"cpm": 9,  "ctr": 0.02,  "conv_rate": 0.04},
        "google": {"cpm": 15, "ctr": 0.04,  "conv_rate": 0.07},
        "tiktok": {"cpm": 7,  "ctr": 0.022, "conv_rate": 0.03},
        "x":      {"cpm": 8,  "ctr": 0.018, "conv_rate": 0.025},
    },
}

# Normalize goal key
goal_key = str(goal).lower()
if goal_key not in DEFAULT_ASSUMPTIONS:
    goal_key = "conversions"

assumptions = DEFAULT_ASSUMPTIONS[goal_key]

# Example channel allocation (you can later make this user-editable)
channel_split = {
    "meta":   0.35,
    "google": 0.40,
    "tiktok": 0.15,
    "x":      0.10,
}

st.caption("Estimates are heuristic and for planning only, not live platform forecasts.")

col_left, col_right = st.columns(2)
with col_left:
    avg_order_value = st.number_input(
        "Avg revenue per conversion ($)",
        min_value=1.0,
        value=50.0,
        step=5.0,
    )
with col_right:
    months = st.slider("Months to project", min_value=1, max_value=12, value=1)

total_budget = float(budget) * months

rows = []
for platform_key, share in channel_split.items():
    spend = total_budget * share
    stats = assumptions[platform_key]

    cpm = stats["cpm"]
    ctr = stats["ctr"]
    conv_rate = stats["conv_rate"]

    # Impressions, Clicks, Conversions
    impressions = (spend / cpm) * 1000 if cpm > 0 else 0
    clicks = impressions * ctr
    conversions = clicks * conv_rate
    revenue = conversions * avg_order_value
    roi = ((revenue - spend) / spend * 100) if spend > 0 else 0

    rows.append({
        "Platform": platform_key.capitalize(),
        "Goal": goal_key.capitalize(),
        "Spend ($)": round(spend, 2),
        "Impressions (est)": int(impressions),
        "Clicks (est)": int(clicks),
        "Conversions (est)": round(conversions, 1),
        "Revenue (est $)": round(revenue, 2),
        "ROI % (est)": round(roi, 1),
    })

roi_df = pd.DataFrame(rows)

st.dataframe(roi_df, use_container_width=True)

# Quick summary line
total_rev = roi_df["Revenue (est $)"].sum()
overall_roi = (total_rev - total_budget) / total_budget * 100 if total_budget > 0 else 0

st.success(
    f"Projected total revenue ≈ **${total_rev:,.0f}** on **${total_budget:,.0f}** spend "
    f"(overall ROI ≈ **{overall_roi:,.1f}%** over {months} month(s))."
)
