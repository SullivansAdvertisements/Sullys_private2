st.subheader("📊 Advanced Trends & Research")

seed_raw = st.text_input(
    "Enter keyword(s) or interests (comma separated)",
    placeholder="streetwear, home care services, independent artist marketing"
)

geo = st.selectbox(
    "Geographic focus",
    ["Worldwide", "US", "UK", "CA", "AU"],
    index=1
)

timeframe = st.selectbox(
    "Timeframe",
    ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
    index=2
)

platform = st.selectbox(
    "Search source",
    ["Web", "YouTube", "News", "Images", "Shopping"],
)

gprop_map = {
    "Web": "",
    "YouTube": "youtube",
    "News": "news",
    "Images": "images",
    "Shopping": "froogle",
}

if st.button("Run Advanced Research"):
    keywords = [k.strip() for k in seed_raw.split(",") if k.strip()]

    if not keywords:
        st.warning("Please enter at least one keyword.")
    else:
        with st.spinner("Pulling advanced trend data..."):
            data = get_advanced_trends(
                keywords=keywords,
                geo="" if geo == "Worldwide" else geo,
                timeframe=timeframe,
                gprop=gprop_map[platform],
            )

        if "error" in data:
            st.error(data["error"])
        else:
            # 📈 Interest over time
            st.markdown("### 📈 Interest Over Time")
            if not data["interest_over_time"].empty:
                st.line_chart(data["interest_over_time"])
            else:
                st.info("No time-series data available.")

            # 🌍 Top locations
            st.markdown("### 🌍 Top Locations by Interest")
            if not data["interest_by_region"].empty:
                st.dataframe(
                    data["interest_by_region"]
                    .sort_values(by=keywords[0], ascending=False)
                    .head(20)
                )
            else:
                st.info("No regional data available.")

            # 🔎 Related queries
            st.markdown("### 🔎 Related & Rising Queries")

            for kw, rq in data["related_queries"].items():
                st.markdown(f"**Keyword:** {kw}")

                if not rq["top"].empty:
                    st.write("Top queries")
                    st.dataframe(rq["top"].head(10))

                if not rq["rising"].empty:
                    st.write("Rising / Breakout queries")
                    st.dataframe(rq["rising"].head(10))