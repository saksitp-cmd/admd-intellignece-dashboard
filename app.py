
import re
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from datetime import datetime, timedelta, date
from streamlit_autorefresh import st_autorefresh

# ============================================================
# API KEYS - STREAMLIT COMMUNITY CLOUD
# Add these in Streamlit Cloud > App > Settings > Secrets
# ============================================================

SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")
OER_APP_ID = st.secrets.get("OER_APP_ID", "")
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", "")
AVIATIONSTACK_API_KEY = st.secrets.get("AVIATIONSTACK_API_KEY", "")

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Phuket Travel Intelligence Command Center",
    page_icon="🛰️",
    layout="wide"
)

st_autorefresh(interval=30 * 60 * 1000, key="auto_refresh")

# ============================================================
# FBI-INSPIRED MODERN UI
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(28, 80, 150, 0.30), transparent 35%),
        radial-gradient(circle at 85% 5%, rgba(18, 190, 180, 0.16), transparent 30%),
        linear-gradient(135deg, #02050A 0%, #07101D 50%, #02050A 100%);
    color: #EAF3FF;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07111F 0%, #03070D 100%);
    border-right: 1px solid rgba(104, 167, 255, 0.18);
}

.intel-header {
    border: 1px solid rgba(86, 160, 255, 0.25);
    background:
        linear-gradient(135deg, rgba(9, 22, 39, 0.92), rgba(4, 9, 16, 0.94)),
        repeating-linear-gradient(
            90deg,
            rgba(255,255,255,0.025) 0px,
            rgba(255,255,255,0.025) 1px,
            transparent 1px,
            transparent 14px
        );
    padding: 26px 28px;
    border-radius: 24px;
    box-shadow: 0 0 30px rgba(0, 102, 255, 0.12);
    margin-bottom: 22px;
}

.intel-title {
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 0.04em;
    color: #EAF4FF;
    text-transform: uppercase;
}

.intel-subtitle {
    font-size: 14px;
    color: #91A8C4;
    margin-top: 4px;
}

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid rgba(100, 170, 255, 0.35);
    color: #A9D2FF;
    background: rgba(28, 95, 170, 0.14);
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
    letter-spacing: 0.05em;
}

.metric-card {
    background: linear-gradient(145deg, rgba(9, 20, 34, 0.96), rgba(14, 29, 50, 0.88));
    border: 1px solid rgba(94, 160, 235, 0.22);
    border-radius: 20px;
    padding: 20px 20px;
    box-shadow: 0 0 22px rgba(15, 115, 255, 0.10);
    min-height: 126px;
}

.metric-label {
    color: #8CA6C2;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    font-weight: 800;
}

.metric-value {
    color: #F3F8FF;
    font-size: 34px;
    font-weight: 900;
    margin-top: 6px;
}

.metric-note {
    color: #7890AA;
    font-size: 12px;
    margin-top: 2px;
}

.news-card {
    background: linear-gradient(145deg, rgba(8, 17, 30, 0.95), rgba(5, 10, 18, 0.95));
    border: 1px solid rgba(105, 165, 245, 0.18);
    border-left: 4px solid #3288FF;
    padding: 16px 18px;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 0 16px rgba(0, 90, 210, 0.08);
}

.card-meta {
    color: #82A1C7;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 800;
}

.card-title {
    font-size: 16px;
    font-weight: 800;
    color: #F5F9FF;
    margin-top: 8px;
    margin-bottom: 6px;
}

.card-snippet {
    color: #B9C7D8;
    font-size: 13px;
    line-height: 1.55;
}

.risk-high {
    color: #FF4D5E;
    font-weight: 900;
}

.risk-medium {
    color: #FFC857;
    font-weight: 900;
}

.risk-low {
    color: #4BE3A4;
    font-weight: 900;
}

a {
    color: #6BB6FF !important;
    text-decoration: none;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# MARKET CONFIGURATION
# ============================================================

MARKETS = {
    "Europe": {
        "UK": "GB",
        "Germany": "DE",
        "France": "FR",
        "Sweden": "SE",
        "Russia": "RU"
    },
    "Oceania": {
        "Australia": "AU",
        "New Zealand": "NZ"
    },
    "Middle East": {
        "Saudi Arabia": "SA",
        "Israel": "IL",
        "UAE": "AE",
        "Qatar": "QA",
        "Kuwait": "KW"
    },
    "South Asia": {
        "India": "IN"
    },
    "East Asia": {
        "China": "CN",
        "South Korea": "KR",
        "Japan": "JP",
        "Hong Kong": "HK",
        "Taiwan": "TW"
    },
    "Southeast Asia": {
        "Singapore": "SG",
        "Malaysia": "MY",
        "Indonesia": "ID",
        "Vietnam": "VN"
    }
}

FOCUS_COUNTRIES = [
    "UK",
    "Australia",
    "New Zealand",
    "Saudi Arabia",
    "India",
    "Russia",
    "Israel",
    "Germany",
    "France",
    "Sweden"
]

COUNTRY_CURRENCY = {
    "UK": "GBP",
    "Australia": "AUD",
    "New Zealand": "NZD",
    "Saudi Arabia": "SAR",
    "India": "INR",
    "Russia": "RUB",
    "Israel": "ILS",
    "Germany": "EUR",
    "France": "EUR",
    "Sweden": "SEK",
    "UAE": "AED",
    "Qatar": "QAR",
    "Kuwait": "KWD",
    "China": "CNY",
    "South Korea": "KRW",
    "Japan": "JPY",
    "Hong Kong": "HKD",
    "Taiwan": "TWD",
    "Singapore": "SGD",
    "Malaysia": "MYR",
    "Indonesia": "IDR",
    "Vietnam": "VND"
}

RISK_KEYWORDS = [
    "war", "conflict", "attack", "strike", "flight cancellation",
    "travel advisory", "warning", "safety", "danger", "accident",
    "flood", "storm", "monsoon", "earthquake", "tsunami",
    "disease", "outbreak", "inflation", "recession", "sanction",
    "airline disruption", "delay", "protest", "unrest", "terror"
]

OPPORTUNITY_KEYWORDS = [
    "new route", "more flights", "visa free", "visa-free",
    "tourism growth", "holiday demand", "school holiday",
    "travel boom", "strong demand", "record arrivals",
    "family travel", "destination wedding", "luxury travel",
    "easter", "eid", "summer holiday", "winter escape"
]

REDDIT_SUBREDDITS = ["ThailandTourism", "phuket", "travel"]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_get(url, params=None, headers=None, timeout=25):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def get_continent(country):
    for continent, countries in MARKETS.items():
        if country in countries:
            return continent
    return "Other"


def country_code(country):
    for _, countries in MARKETS.items():
        if country in countries:
            return countries[country]
    return "US"


def classify_signal(text):
    text_l = clean_text(text).lower()
    risk_score = sum(1 for keyword in RISK_KEYWORDS if keyword in text_l)
    opportunity_score = sum(1 for keyword in OPPORTUNITY_KEYWORDS if keyword in text_l)

    if risk_score >= 2:
        risk = "High"
    elif risk_score == 1:
        risk = "Medium"
    else:
        risk = "Low"

    if opportunity_score >= 1 and risk_score == 0:
        impact = "Positive"
    elif risk_score >= 1:
        impact = "Negative"
    else:
        impact = "Neutral"

    return risk, impact


def sentiment_score(text):
    text_l = clean_text(text).lower()

    positive_words = [
        "love", "amazing", "good", "great", "beautiful", "safe",
        "recommend", "best", "fun", "family", "easy", "worth",
        "excited", "booked", "enjoy", "perfect"
    ]

    negative_words = [
        "bad", "unsafe", "scam", "expensive", "rain", "worried",
        "avoid", "cancel", "danger", "problem", "crowded", "delay",
        "strike", "fear", "sick", "dirty"
    ]

    positive = sum(1 for word in positive_words if word in text_l)
    negative = sum(1 for word in negative_words if word in text_l)

    if positive > negative:
        return "Positive"
    elif negative > positive:
        return "Negative"
    return "Neutral"


def date_window_to_serp_tbs(start_date, end_date):
    days = (end_date - start_date).days

    if days <= 1:
        return "qdr:d"
    if days <= 7:
        return "qdr:w"
    if days <= 31:
        return "qdr:m"
    if days <= 365:
        return "qdr:y"

    return None


def build_market_queries(country):
    return [
        f"{country} travelers Phuket Thailand tourism",
        f"{country} Thailand travel advisory Phuket",
        f"{country} flights to Phuket Thailand",
        f"{country} Thailand visa travel news",
        f"{country} Phuket holiday demand"
    ]


def build_trend_queries():
    return [
        "Phuket holiday",
        "Thailand holiday",
        "Phuket family vacation",
        "water park Phuket",
        "Andamanda Phuket"
    ]

# ============================================================
# DATA SOURCE FUNCTIONS
# ============================================================

@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def fetch_serp_news(api_key, country, start_date, end_date):
    if not api_key:
        return []

    rows = []
    tbs = date_window_to_serp_tbs(start_date, end_date)

    for query in build_market_queries(country):
        params = {
            "engine": "google_news",
            "q": query,
            "api_key": api_key,
            "hl": "en",
            "gl": country_code(country).lower(),
            "num": 10
        }

        if tbs:
            params["tbs"] = tbs

        data = safe_get("https://serpapi.com/search.json", params=params)

        if not data:
            continue

        for item in data.get("news_results", []):
            title = clean_text(item.get("title", ""))
            snippet = clean_text(item.get("snippet", ""))
            source = item.get("source", "")
            link = item.get("link", "")
            date_text = item.get("date", "")

            risk, impact = classify_signal(f"{title} {snippet}")

            rows.append({
                "source_type": "SERP Google News",
                "continent": get_continent(country),
                "country": country,
                "query": query,
                "title": title,
                "snippet": snippet,
                "source": source,
                "link": link,
                "date_text": date_text,
                "risk": risk,
                "impact": impact
            })

        time.sleep(0.15)

    return rows


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def fetch_newsapi(api_key, country, start_date, end_date):
    if not api_key:
        return []

    rows = []

    for query in build_market_queries(country):
        params = {
            "q": query,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 20,
            "apiKey": api_key
        }

        data = safe_get("https://newsapi.org/v2/everything", params=params)

        if not data:
            continue

        for item in data.get("articles", []):
            title = clean_text(item.get("title", ""))
            snippet = clean_text(item.get("description", ""))
            source_obj = item.get("source", {}) or {}
            source = source_obj.get("name", "")
            link = item.get("url", "")
            date_text = item.get("publishedAt", "")

            risk, impact = classify_signal(f"{title} {snippet}")

            rows.append({
                "source_type": "NewsAPI",
                "continent": get_continent(country),
                "country": country,
                "query": query,
                "title": title,
                "snippet": snippet,
                "source": source,
                "link": link,
                "date_text": date_text,
                "risk": risk,
                "impact": impact
            })

        time.sleep(0.15)

    return rows


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def fetch_gdelt(country, start_date, end_date):
    rows = []

    start_dt = datetime.combine(start_date, datetime.min.time()).strftime("%Y%m%d%H%M%S")
    end_dt = datetime.combine(end_date, datetime.max.time()).strftime("%Y%m%d%H%M%S")

    for query in build_market_queries(country):
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": 20,
            "sort": "HybridRel",
            "startdatetime": start_dt,
            "enddatetime": end_dt
        }

        data = safe_get("https://api.gdeltproject.org/api/v2/doc/doc", params=params)

        if not data:
            continue

        for item in data.get("articles", []):
            title = clean_text(item.get("title", ""))
            source = item.get("domain", "")
            link = item.get("url", "")
            date_text = item.get("seendate", "")

            risk, impact = classify_signal(title)

            rows.append({
                "source_type": "GDELT",
                "continent": get_continent(country),
                "country": country,
                "query": query,
                "title": title,
                "snippet": date_text,
                "source": source,
                "link": link,
                "date_text": date_text,
                "risk": risk,
                "impact": impact
            })

        time.sleep(0.15)

    return rows


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_serp_trends(api_key, countries):
    if not api_key:
        return pd.DataFrame()

    rows = []

    for country in countries:
        for keyword in build_trend_queries():
            params = {
                "engine": "google_trends",
                "q": keyword,
                "api_key": api_key,
                "geo": country_code(country),
                "date": "today 3-m",
                "data_type": "TIMESERIES"
            }

            data = safe_get("https://serpapi.com/search.json", params=params)

            if not data:
                continue

            timeline = (data.get("interest_over_time", {}) or {}).get("timeline_data", [])

            for point in timeline:
                date_label = point.get("date", "")
                values = point.get("values", [])

                if not values:
                    continue

                raw_value = values[0].get("value", 0)

                try:
                    value = float(raw_value)
                except Exception:
                    value = 0.0

                rows.append({
                    "country": country,
                    "continent": get_continent(country),
                    "keyword": keyword,
                    "date": date_label,
                    "interest": value
                })

            time.sleep(0.15)

    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_weather(api_key):
    if not api_key:
        return pd.DataFrame()

    params = {
        "q": "Phuket,TH",
        "appid": api_key,
        "units": "metric"
    }

    data = safe_get("https://api.openweathermap.org/data/2.5/forecast", params=params)

    if not data:
        return pd.DataFrame()

    rows = []

    for item in data.get("list", []):
        weather_list = item.get("weather", [{}])
        weather_desc = weather_list[0].get("description", "") if weather_list else ""

        rain = item.get("rain", {}).get("3h", 0)
        wind = item.get("wind", {}).get("speed", 0)
        temp = item.get("main", {}).get("temp", None)
        humidity = item.get("main", {}).get("humidity", None)

        risk = "Low"

        if rain >= 10 or wind >= 12:
            risk = "High"
        elif rain >= 3 or wind >= 8:
            risk = "Medium"

        rows.append({
            "datetime": item.get("dt_txt"),
            "temperature_c": temp,
            "humidity": humidity,
            "rain_3h_mm": rain,
            "wind_mps": wind,
            "description": weather_desc,
            "weather_risk": risk
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_exchange_rates_oer(app_id, countries):
    if not app_id:
        return pd.DataFrame()

    params = {
        "app_id": app_id
    }

    data = safe_get("https://openexchangerates.org/api/latest.json", params=params)

    if not data:
        return pd.DataFrame()

    rates = data.get("rates", {})

    if "THB" not in rates:
        return pd.DataFrame()

    usd_to_thb = rates["THB"]
    rows = []

    for country in countries:
        currency = COUNTRY_CURRENCY.get(country)

        if not currency:
            continue

        if currency not in rates:
            continue

        usd_to_currency = rates[currency]

        if usd_to_currency == 0:
            continue

        currency_to_thb = usd_to_thb / usd_to_currency

        rows.append({
            "country": country,
            "continent": get_continent(country),
            "currency": currency,
            "to_thb": round(currency_to_thb, 4),
            "updated_timestamp": data.get("timestamp", "")
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_youtube(api_key, countries):
    if not api_key:
        return pd.DataFrame()

    rows = []

    for country in countries:
        query = f"Phuket Thailand travel {country}"

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "date",
            "maxResults": 10,
            "key": api_key
        }

        data = safe_get("https://www.googleapis.com/youtube/v3/search", params=params)

        if not data:
            continue

        video_ids = []
        meta = {}

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            snippet = item.get("snippet", {}) or {}

            video_ids.append(video_id)
            meta[video_id] = {
                "country": country,
                "continent": get_continent(country),
                "title": clean_text(snippet.get("title", "")),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }

        if video_ids:
            stats_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": api_key
            }

            stats_data = safe_get("https://www.googleapis.com/youtube/v3/videos", params=stats_params)

            if stats_data:
                for item in stats_data.get("items", []):
                    video_id = item.get("id")
                    stats = item.get("statistics", {}) or {}
                    m = meta.get(video_id, {})

                    rows.append({
                        **m,
                        "views": int(stats.get("viewCount", 0) or 0),
                        "likes": int(stats.get("likeCount", 0) or 0),
                        "comments": int(stats.get("commentCount", 0) or 0)
                    })

        time.sleep(0.2)

    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_reddit(countries):
    rows = []
    headers = {"User-Agent": "PhuketTravelIntelDashboard/1.0"}

    for country in countries:
        query = f"Phuket Thailand travel {country}"

        for subreddit in REDDIT_SUBREDDITS:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"

            params = {
                "q": query,
                "restrict_sr": "true",
                "sort": "new",
                "limit": 10
            }

            data = safe_get(url, params=params, headers=headers, timeout=20)

            if not data:
                continue

            children = data.get("data", {}).get("children", [])

            for child in children:
                d = child.get("data", {}) or {}

                title = clean_text(d.get("title", ""))
                body = clean_text(d.get("selftext", ""))

                risk, impact = classify_signal(f"{title} {body}")
                sentiment = sentiment_score(f"{title} {body}")

                permalink = d.get("permalink", "")

                rows.append({
                    "country": country,
                    "continent": get_continent(country),
                    "subreddit": subreddit,
                    "title": title,
                    "snippet": body[:300],
                    "score": d.get("score", 0),
                    "comments": d.get("num_comments", 0),
                    "sentiment": sentiment,
                    "risk": risk,
                    "impact": impact,
                    "url": f"https://www.reddit.com{permalink}" if permalink else ""
                })

            time.sleep(0.35)

    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_aviationstack(api_key):
    if not api_key:
        return pd.DataFrame()

    params = {
        "access_key": api_key,
        "arr_iata": "HKT",
        "limit": 100
    }

    data = safe_get("http://api.aviationstack.com/v1/flights", params=params)

    if not data:
        return pd.DataFrame()

    rows = []

    for item in data.get("data", []):
        airline = item.get("airline", {}) or {}
        departure = item.get("departure", {}) or {}
        arrival = item.get("arrival", {}) or {}
        flight = item.get("flight", {}) or {}

        rows.append({
            "airline": airline.get("name", ""),
            "flight_number": flight.get("iata", ""),
            "from_airport": departure.get("airport", ""),
            "from_iata": departure.get("iata", ""),
            "to_airport": arrival.get("airport", ""),
            "to_iata": arrival.get("iata", ""),
            "status": item.get("flight_status", ""),
            "arrival_time": arrival.get("scheduled", "")
        })

    return pd.DataFrame(rows)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 🛰️ Intelligence Control")

selected_continents = st.sidebar.multiselect(
    "Continents",
    list(MARKETS.keys()),
    default=["Europe", "Oceania", "Middle East", "South Asia"]
)

available_countries = []

for continent in selected_continents:
    available_countries.extend(list(MARKETS[continent].keys()))

default_countries = [
    country for country in FOCUS_COUNTRIES
    if country in available_countries
]

selected_countries = st.sidebar.multiselect(
    "Countries",
    available_countries,
    default=default_countries
)

today = date.today()
default_start = today - timedelta(days=90)

date_range = st.sidebar.date_input(
    "News / Event Date Range",
    value=(default_start, today)
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start, today

sources = st.sidebar.multiselect(
    "Data Sources",
    [
        "SERP News",
        "SERP Trends",
        "NewsAPI",
        "GDELT",
        "OpenWeather",
        "Open Exchange Rates",
        "YouTube",
        "Reddit",
        "AviationStack"
    ],
    default=[
        "SERP News",
        "SERP Trends",
        "NewsAPI",
        "GDELT",
        "OpenWeather",
        "Open Exchange Rates",
        "YouTube",
        "Reddit",
        "AviationStack"
    ]
)

run_scan = st.sidebar.button(
    "Run Weekly Intelligence Scan",
    use_container_width=True
)

st.sidebar.divider()
st.sidebar.markdown("### API Status")

st.sidebar.write("SERP:", "✅" if SERP_API_KEY else "❌")
st.sidebar.write("NewsAPI:", "✅" if NEWS_API_KEY else "❌")
st.sidebar.write("OpenWeather:", "✅" if OPENWEATHER_API_KEY else "❌")
st.sidebar.write("Open Exchange Rates:", "✅" if OER_APP_ID else "❌")
st.sidebar.write("YouTube:", "✅" if YOUTUBE_API_KEY else "❌")
st.sidebar.write("AviationStack:", "✅" if AVIATIONSTACK_API_KEY else "❌")

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="intel-header">
    <div>
        <span class="badge">PHUKET</span>
        <span class="badge">TRAVEL INTELLIGENCE</span>
        <span class="badge">WEEKLY COMMAND CENTER</span>
    </div>
    <div class="intel-title">Tourism Intelligence Dashboard</div>
    <div class="intel-subtitle">
        Demand signals, risk events, search behavior, social sentiment, weather risk, currency strength and travel momentum for Andamanda Phuket
    </div>
</div>
""", unsafe_allow_html=True)

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

# ============================================================
# DATA LOADING
# ============================================================

if run_scan or "loaded_once" not in st.session_state:
    with st.spinner("Running weekly intelligence scan..."):

        signal_rows = []

        if "SERP News" in sources:
            for country in selected_countries:
                signal_rows.extend(fetch_serp_news(SERP_API_KEY, country, start_date, end_date))

        if "NewsAPI" in sources:
            for country in selected_countries:
                signal_rows.extend(fetch_newsapi(NEWS_API_KEY, country, start_date, end_date))

        if "GDELT" in sources:
            for country in selected_countries:
                signal_rows.extend(fetch_gdelt(country, start_date, end_date))

        signals_df = pd.DataFrame(signal_rows)

        if not signals_df.empty:
            signals_df["risk_score"] = signals_df["risk"].map({
                "Low": 1,
                "Medium": 2,
                "High": 3
            })

            signals_df["impact_score"] = signals_df["impact"].map({
                "Negative": -1,
                "Neutral": 0,
                "Positive": 1
            })

            signals_df = signals_df.drop_duplicates(
                subset=["country", "title", "link"],
                keep="first"
            )

        trends_df = fetch_serp_trends(SERP_API_KEY, selected_countries) if "SERP Trends" in sources else pd.DataFrame()
        weather_df = fetch_weather(OPENWEATHER_API_KEY) if "OpenWeather" in sources else pd.DataFrame()
        exchange_df = fetch_exchange_rates_oer(OER_APP_ID, selected_countries) if "Open Exchange Rates" in sources else pd.DataFrame()
        youtube_df = fetch_youtube(YOUTUBE_API_KEY, selected_countries) if "YouTube" in sources else pd.DataFrame()
        reddit_df = fetch_reddit(selected_countries) if "Reddit" in sources else pd.DataFrame()
        flight_df = fetch_aviationstack(AVIATIONSTACK_API_KEY) if "AviationStack" in sources else pd.DataFrame()

        st.session_state["signals_df"] = signals_df
        st.session_state["trends_df"] = trends_df
        st.session_state["weather_df"] = weather_df
        st.session_state["exchange_df"] = exchange_df
        st.session_state["youtube_df"] = youtube_df
        st.session_state["reddit_df"] = reddit_df
        st.session_state["flight_df"] = flight_df
        st.session_state["loaded_once"] = True

signals_df = st.session_state.get("signals_df", pd.DataFrame())
trends_df = st.session_state.get("trends_df", pd.DataFrame())

# Fix for Streamlit Cloud / Pandas Arrow dtype:
# Google Trends values may arrive as text, so convert before mean/max/last aggregation.
if not trends_df.empty and "interest" in trends_df.columns:
    trends_df["interest"] = pd.to_numeric(trends_df["interest"], errors="coerce").fillna(0.0)

weather_df = st.session_state.get("weather_df", pd.DataFrame())
exchange_df = st.session_state.get("exchange_df", pd.DataFrame())
youtube_df = st.session_state.get("youtube_df", pd.DataFrame())
reddit_df = st.session_state.get("reddit_df", pd.DataFrame())
flight_df = st.session_state.get("flight_df", pd.DataFrame())

# ============================================================
# KPI CALCULATION
# ============================================================

total_signals = len(signals_df)

if not signals_df.empty:
    high_risk = len(signals_df[signals_df["risk"] == "High"])
    positive_signals = len(signals_df[signals_df["impact"] == "Positive"])
    negative_signals = len(signals_df[signals_df["impact"] == "Negative"])
else:
    high_risk = 0
    positive_signals = 0
    negative_signals = 0

health_score = round(
    max(
        0,
        min(
            100,
            75 + positive_signals * 1.2 - negative_signals * 1.5 - high_risk * 3
        )
    )
)

if health_score >= 75:
    health_status = "Strong / Opportunity"
    health_class = "risk-low"
elif health_score >= 55:
    health_status = "Monitor"
    health_class = "risk-medium"
else:
    health_status = "Risk Watch"
    health_class = "risk-high"

# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Phuket Demand Outlook</div>
        <div class="metric-value">{health_score}</div>
        <div class="metric-note"><span class="{health_class}">{health_status}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Intelligence Signals</div>
        <div class="metric-value">{total_signals}</div>
        <div class="metric-note">News + macro events</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">High-Risk Alerts</div>
        <div class="metric-value"><span class="risk-high">{high_risk}</span></div>
        <div class="metric-note">Safety / disruption / macro risks</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Markets Tracked</div>
        <div class="metric-value">{len(selected_countries)}</div>
        <div class="metric-note">Country-level weekly scan</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Brief",
    "Country Intelligence",
    "Search Trends",
    "Social & YouTube",
    "Weather / Currency / Flights",
    "Raw Intelligence Feed"
])

# ============================================================
# TAB 1
# ============================================================

with tab1:
    st.subheader("Weekly Executive Brief")

    if signals_df.empty:
        st.warning("No news or event data loaded. Check Streamlit Secrets and click Run Weekly Intelligence Scan.")
    else:
        summary = signals_df.groupby(["continent", "country"]).agg(
            total_signals=("title", "count"),
            high_risk=("risk", lambda x: (x == "High").sum()),
            medium_risk=("risk", lambda x: (x == "Medium").sum()),
            positive=("impact", lambda x: (x == "Positive").sum()),
            negative=("impact", lambda x: (x == "Negative").sum()),
            avg_risk=("risk_score", "mean")
        ).reset_index()

        summary["situation"] = summary.apply(
            lambda r:
                "Opportunity" if r["positive"] > r["negative"] and r["high_risk"] == 0
                else "Risk Watch" if r["high_risk"] > 0
                else "Stable / Monitor",
            axis=1
        )

        summary["recommendation"] = summary.apply(
            lambda r:
                "Increase marketing push" if r["positive"] > r["negative"] and r["avg_risk"] < 2
                else "Monitor before scaling spend" if r["avg_risk"] < 2.5
                else "Hold aggressive campaigns / monitor risk",
            axis=1
        )

        st.dataframe(
            summary.sort_values(["high_risk", "positive"], ascending=[False, False]),
            use_container_width=True,
            hide_index=True
        )

        c1, c2 = st.columns(2)

        with c1:
            fig = px.bar(
                summary,
                x="country",
                y=["positive", "negative"],
                title="Positive vs Negative Signals by Country",
                template="plotly_dark",
                barmode="group"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            risk_chart = signals_df.groupby(["country", "risk"]).size().reset_index(name="count")

            fig = px.bar(
                risk_chart,
                x="country",
                y="count",
                color="risk",
                title="Risk Signals by Country",
                template="plotly_dark",
                barmode="stack"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 2
# ============================================================

with tab2:
    st.subheader("Country-Level Intelligence")

    country_view = st.selectbox("Select country", selected_countries)

    country_signals = signals_df[signals_df["country"] == country_view] if not signals_df.empty and "country" in signals_df.columns else pd.DataFrame()
    country_reddit = reddit_df[reddit_df["country"] == country_view] if not reddit_df.empty and "country" in reddit_df.columns else pd.DataFrame()
    country_youtube = youtube_df[youtube_df["country"] == country_view] if not youtube_df.empty and "country" in youtube_df.columns else pd.DataFrame()

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("News / Event Signals", len(country_signals))

    with col_b:
        st.metric("Reddit Mentions", len(country_reddit))

    with col_c:
        st.metric("YouTube Videos", len(country_youtube))

    if not country_signals.empty:
        st.markdown("### Most Important News / Events")

        top_country = country_signals.sort_values(["risk_score"], ascending=False).head(15)

        for _, row in top_country.iterrows():
            risk_class = {
                "High": "risk-high",
                "Medium": "risk-medium",
                "Low": "risk-low"
            }.get(row["risk"], "risk-low")

            st.markdown(f"""
            <div class="news-card">
                <div class="card-meta">{row['source_type']} / {row['country']} / {row['source']} / {row['date_text']}</div>
                <div class="card-title">{row['title']}</div>
                <div class="card-snippet">{row['snippet']}</div>
                <div class="card-snippet">Risk: <span class="{risk_class}">{row['risk']}</span> | Impact: {row['impact']}</div>
                <a href="{row['link']}" target="_blank">Open source</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No country news/event signals found.")

# ============================================================
# TAB 3
# ============================================================

with tab3:
    st.subheader("Search Trend Demand Signals")

    if trends_df.empty:
        st.info("No trend data loaded. SERP API key is required.")
    else:
        trend_countries = sorted(trends_df["country"].unique())

        trend_country = st.multiselect(
            "Filter trend countries",
            trend_countries,
            default=trend_countries[:5]
        )

        trend_filtered = trends_df[trends_df["country"].isin(trend_country)].copy()

        if not trend_filtered.empty and "interest" in trend_filtered.columns:
            trend_filtered["interest"] = pd.to_numeric(
                trend_filtered["interest"],
                errors="coerce"
            ).fillna(0.0)

        if trend_filtered.empty:
            st.info("No trend rows found for the selected countries.")
            st.stop()

        fig = px.line(
            trend_filtered,
            x="date",
            y="interest",
            color="country",
            line_dash="keyword",
            title="Search Interest Over Time",
            template="plotly_dark"
        )

        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        trend_summary = trend_filtered.groupby(["country", "keyword"]).agg(
            avg_interest=("interest", "mean"),
            max_interest=("interest", "max"),
            latest_interest=("interest", "last")
        ).reset_index()

        st.dataframe(
            trend_summary.sort_values("latest_interest", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# TAB 4
# ============================================================

with tab4:
    st.subheader("Traveler Sentiment and Video Momentum")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Reddit Traveler Listening")

        if reddit_df.empty:
            st.info("No Reddit data loaded.")
        else:
            reddit_summary = reddit_df.groupby(["country", "sentiment"]).size().reset_index(name="mentions")

            fig = px.bar(
                reddit_summary,
                x="country",
                y="mentions",
                color="sentiment",
                title="Reddit Sentiment by Country",
                template="plotly_dark"
            )

            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            reddit_cols = [
                "country",
                "subreddit",
                "title",
                "sentiment",
                "risk",
                "score",
                "comments",
                "url"
            ]

            st.dataframe(
                reddit_df[reddit_cols].head(50),
                use_container_width=True,
                hide_index=True
            )

    with c2:
        st.markdown("### YouTube Phuket Travel Momentum")

        if youtube_df.empty:
            st.info("No YouTube data loaded. YouTube API key is required.")
        else:
            yt_summary = youtube_df.groupby("country").agg(
                videos=("title", "count"),
                total_views=("views", "sum"),
                total_comments=("comments", "sum"),
                avg_views=("views", "mean")
            ).reset_index()

            fig = px.bar(
                yt_summary.sort_values("total_views", ascending=False),
                x="country",
                y="total_views",
                title="Recent YouTube Views by Market Query",
                template="plotly_dark"
            )

            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            youtube_cols = [
                "country",
                "title",
                "channel",
                "views",
                "likes",
                "comments",
                "published_at",
                "url"
            ]

            st.dataframe(
                youtube_df[youtube_cols]
                .sort_values("views", ascending=False)
                .head(50),
                use_container_width=True,
                hide_index=True
            )

# ============================================================
# TAB 5
# ============================================================

with tab5:
    st.subheader("Weather Risk, Currency Strength and Flight Intelligence")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Phuket Weather Risk")

        if weather_df.empty:
            st.info("No weather data loaded. OpenWeather API key is required.")
        else:
            weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

            fig = px.bar(
                weather_df,
                x="datetime",
                y="rain_3h_mm",
                color="weather_risk",
                title="Phuket Rain Forecast Risk",
                template="plotly_dark"
            )

            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                weather_df,
                use_container_width=True,
                hide_index=True
            )

    with c2:
        st.markdown("### Currency Strength vs Thai Baht")

        if exchange_df.empty:
            st.info("No currency data loaded. Open Exchange Rates App ID is required.")
        else:
            fig = px.bar(
                exchange_df.sort_values("to_thb", ascending=False),
                x="currency",
                y="to_thb",
                color="country",
                title="Source Market Currency to THB",
                template="plotly_dark"
            )

            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                exchange_df,
                use_container_width=True,
                hide_index=True
            )

    st.markdown("### HKT Arrival Flight Intelligence")

    if flight_df.empty:
        st.info("No flight data loaded. AviationStack is optional.")
    else:
        st.dataframe(
            flight_df,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# TAB 6
# ============================================================

with tab6:
    st.subheader("Raw Intelligence Feed")

    if signals_df.empty:
        st.info("No raw news/event feed.")
    else:
        feed_countries = sorted(signals_df["country"].unique())

        feed_filter_country = st.multiselect(
            "Filter countries",
            feed_countries,
            default=feed_countries
        )

        feed_filter_risk = st.multiselect(
            "Filter risk level",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )

        feed = signals_df[
            signals_df["country"].isin(feed_filter_country)
            & signals_df["risk"].isin(feed_filter_risk)
        ].copy()

        feed_cols = [
            "source_type",
            "continent",
            "country",
            "title",
            "snippet",
            "source",
            "date_text",
            "risk",
            "impact",
            "link"
        ]

        st.dataframe(
            feed[feed_cols].head(500),
            use_container_width=True,
            hide_index=True
        )

        csv = feed.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Filtered Intelligence CSV",
            data=csv,
            file_name="phuket_travel_intelligence_weekly.csv",
            mime="text/csv"
        )
