# 🌺 Sully’s Multi-Platform Media Planner

A **Streamlit AI-powered advertising bot** for managing and generating cross-platform campaigns across **Meta**, **Google/YouTube**, **TikTok**, and **Spotify** — with integrated keyword & trends research via **Google Trends**.

When shared through messaging apps or social media, your custom logo appears as the preview icon ✅

---

## 🧠 Features

| Area | Description |
|------|--------------|
| **Strategy Planner** | Generates multi-platform ad strategies by niche (Music, Clothing, Homecare). |
| **Google / YouTube Tab** | Keyword + landing-page planner; connects to Google Ads / YouTube APIs. |
| **TikTok Tab** | Builds short-form ad creative ideas and hooks. |
| **Spotify Tab** | Plans audio ads with 30-second scripts. |
| **Meta Tab** | Tests token connection and prepares campaign / ad-set / ad creation via Graph API. |
| **Google Trends Integration** | Keyword trend discovery with charts. |
| **Expandable Clients** | Modular `/clients/` folder for future API automation. |

---

## 📁 Repo Structure

```bash
sullys_media_planner/
│
├── streamlit_app.py # main Streamlit app
├── clients/ # modular API clients
│ ├── __init__.py
│ ├── google_client.py
│ ├── tiktok_client.py
│ ├── spotify_client.py
│ └── meta_client.py
│
├── assets/
│ ├── sullivans_logo.png # logo shown in header/sidebar
│ └── og_logo.png # logo for link preview (see below)
│
├── requirements.txt
└── README.md
