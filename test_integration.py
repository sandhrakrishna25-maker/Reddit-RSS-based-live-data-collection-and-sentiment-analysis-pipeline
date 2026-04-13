import unittest
import sqlite3
import pandas as pd
import os
import reddit_data_flask
from reddit_data_flask import app


class TestFlaskIntegration(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True

        self.test_db = "test_integration.db"
        reddit_data_flask.DB_PATH = self.test_db

        conn = sqlite3.connect(self.test_db)

        df = pd.DataFrame({
            "subreddit": ["news"],
            "title": ["Sample integration test title"],
            "link": ["http://example.com"],
            "published": ["2024-01-01"],
            "summary": ["sample summary"],
            "fetched_at": ["2024-01-01 10:00:00"],
            "sentiment_score": [0.75],
            "sentiment_category": ["positive"]
        })

        df.to_sql("reddit_pipeline_Sentmnt_Table", conn, if_exists="replace", index=False)
        conn.close()

        self.client = app.test_client()

    def test_dashboard_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reddit Sentiment Analysis Dashboard", response.data)
        self.assertIn(b"Total Records", response.data)
        self.assertIn(b"Average Score", response.data)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)


if __name__ == "__main__":
    unittest.main()