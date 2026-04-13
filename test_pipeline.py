import unittest
import pandas as pd
import sqlite3
import os

def load_data_for_test(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM reddit_pipeline_Sentmnt_Table", conn)
    conn.close()

    if "sentiment_score" in df.columns:
        df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")

    return df


class TestDataLoading(unittest.TestCase):
    def setUp(self):
        self.db_path = "test.db"
        conn = sqlite3.connect(self.db_path)

        df = pd.DataFrame({
            "subreddit": ["test"],
            "title": ["sample title"],
            "link": ["http://test.com"],
            "published": ["2024"],
            "summary": ["sample summary"],
            "fetched_at": ["2024-01-01 10:00:00"],
            "sentiment_score": ["0.5"],
            "sentiment_category": ["positive"]
        })

        df.to_sql("reddit_pipeline_Sentmnt_Table", conn, if_exists="replace", index=False)
        conn.close()

    def test_load_data(self):
        df = load_data_for_test(self.db_path)
        self.assertFalse(df.empty)
        self.assertIn("sentiment_score", df.columns)
        self.assertEqual(len(df), 1)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)


class TestTransformations(unittest.TestCase):
    def test_sentiment_conversion(self):
        df = pd.DataFrame({
            "sentiment_score": ["0.5", "-0.2"]
        })

        df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")
        self.assertEqual(str(df["sentiment_score"].dtype), "float64")


if __name__ == "__main__":
    unittest.main()