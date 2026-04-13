from flask import Flask, render_template_string
import sqlite3
import pandas as pd

app = Flask(__name__)

DB_PATH = "reddit_pipeline_Sentmnt.db"
TABLE_NAME = "reddit_pipeline_Sentmnt_Table"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()

    if "sentiment_score" in df.columns:
        df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")

    return df


@app.route("/")
def dashboard():
    df = load_data()

    if df.empty:
        return "<h2>No data found in database.</h2>"

    total_rows = len(df)

    sentiment_counts = (
        df["sentiment_category"]
        .value_counts()
        .reset_index()
    )
    sentiment_counts.columns = ["sentiment_category", "count"]

    avg_score = round(df["sentiment_score"].mean(), 3)

    top_positive = df.sort_values(by="sentiment_score", ascending=False).head(5)
    top_negative = df.sort_values(by="sentiment_score", ascending=True).head(5)

    subreddit_summary = (
        df.groupby("subreddit")["sentiment_score"]
        .agg(["count", "mean"])
        .reset_index()
        .sort_values(by="mean", ascending=False)
    )
    subreddit_summary["mean"] = subreddit_summary["mean"].round(3)

    recent_posts = df.sort_values(by="fetched_at", ascending=False).head(20)

    high_positive = df[df["sentiment_score"] >= 0.5].sort_values(by="sentiment_score", ascending=False).head(10)
    high_negative = df[df["sentiment_score"] <= -0.5].sort_values(by="sentiment_score", ascending=True).head(10)

    positive_count = int((df["sentiment_category"] == "positive").sum())
    negative_count = int((df["sentiment_category"] == "negative").sum())
    neutral_count = int((df["sentiment_category"] == "neutral").sum())

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reddit Sentiment Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 30px;
                background-color: #f4f6f8;
                color: #222;
            }
            h1, h2 {
                color: #1f3b5b;
            }
            .cards {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                min-width: 220px;
            }
            .highlight-positive {
                color: green;
                font-weight: bold;
            }
            .highlight-negative {
                color: red;
                font-weight: bold;
            }
            .highlight-neutral {
                color: #666;
                font-weight: bold;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                background: white;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                vertical-align: top;
            }
            th {
                background-color: #1f3b5b;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .section {
                margin-bottom: 40px;
            }
            a {
                color: #1a73e8;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Reddit Sentiment Analysis Dashboard</h1>

        <div class="cards">
            <div class="card"><h3>Total Records</h3><p>{{ total_rows }}</p></div>
            <div class="card"><h3>Average Score</h3><p>{{ avg_score }}</p></div>
            <div class="card"><h3>Positive</h3><p>{{ positive_count }}</p></div>
            <div class="card"><h3>Negative</h3><p>{{ negative_count }}</p></div>
            <div class="card"><h3>Neutral</h3><p>{{ neutral_count }}</p></div>
        </div>

        <h2>Recent Posts</h2>
        <table>
            <tr>
                <th>Subreddit</th>
                <th>Title</th>
                <th>Score</th>
                <th>Category</th>
            </tr>
            {% for _, row in recent_posts.iterrows() %}
            <tr>
                <td>{{ row['subreddit'] }}</td>
                <td><a href="{{ row['link'] }}" target="_blank">{{ row['title'] }}</a></td>
                <td>{{ row['sentiment_score'] }}</td>
                <td>
                    {% if row['sentiment_category'] == 'positive' %}
                        <span class="highlight-positive">{{ row['sentiment_category'] }}</span>
                    {% elif row['sentiment_category'] == 'negative' %}
                        <span class="highlight-negative">{{ row['sentiment_category'] }}</span>
                    {% else %}
                        <span class="highlight-neutral">{{ row['sentiment_category'] }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>

    </body>
    </html>
    """

    return render_template_string(
        html,
        total_rows=total_rows,
        avg_score=avg_score,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        recent_posts=recent_posts
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)