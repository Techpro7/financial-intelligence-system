from financial_news_intel.core.models import ConsolidatedStory
from typing import Dict, Any, List
import sqlite3 # Using SQLite for simplicity/mocking; replace with psycopg2 for PostgreSQL

class DatabaseService:
    def __init__(self, db_path="financial_intel.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._initialize_db()
        print("Structured DB Service Initialized (SQLite)")
    
    def _initialize_db(self):
        cursor = self.conn.cursor()
        
        # 1. Create Stories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Stories (
                story_id TEXT PRIMARY KEY,
                story_text TEXT NOT NULL,
                sentiment TEXT,
                companies_json TEXT,
                sectors_json TEXT,
                regulators_json TEXT,
                vector_id TEXT
            );
        """)
        
        # 2. Create Stock_Impacts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Stock_Impacts (
                impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id TEXT,
                company_name TEXT,
                stock_ticker TEXT,
                impact_direction TEXT,
                confidence REAL,
                impact_type TEXT,
                FOREIGN KEY (story_id) REFERENCES Stories(story_id)
            );
        """)
        self.conn.commit()

    def save_story(self, story: ConsolidatedStory) -> str:
        """Saves a ConsolidatedStory and its related impacts to the SQL tables."""
        cursor = self.conn.cursor()
        
        # A. Insert into Stories Table
        story_id = story.unique_story_id
        
        cursor.execute("""
            INSERT INTO Stories (story_id, story_text, sentiment, companies_json, sectors_json, regulators_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            story_id,
            story.text,
            story.sentiment,
            str(story.entities.companies), # Simple string representation of list for SQLite TEXT
            str(story.entities.sectors),
            str(story.entities.regulators)
        ))
        
        # B. Insert into Stock_Impacts Table
        for impact in story.impacted_stocks:
            cursor.execute("""
                INSERT INTO Stock_Impacts (story_id, company_name, stock_ticker, impact_direction, confidence, impact_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                story_id,
                impact.company_name,
                impact.stock_ticker,
                impact.impact_direction.value,
                impact.confidence,
                impact.type.value
            ))

        self.conn.commit()
        return story_id # Return the story ID which serves as the primary key
    
    def fetch_all_stories_with_impacts(self):
        """Fetches all stories and their related stock impacts."""
        cursor = self.conn.cursor()
        
        # 1. Fetch all stories
        stories_query = "SELECT story_id, sentiment, companies_json FROM Stories"
        cursor.execute(stories_query)
        stories = cursor.fetchall()
        
        results = []
        for story_id, sentiment, companies_json in stories:
            # 2. Fetch impacts for each story
            impacts_query = "SELECT stock_ticker, impact_direction, confidence FROM Stock_Impacts WHERE story_id = ?"
            cursor.execute(impacts_query, (story_id,))
            impacts = cursor.fetchall()
            
            results.append({
                "story_id": story_id[:8] + "...",
                "sentiment": sentiment,
                "companies": companies_json,
                "impacts_count": len(impacts),
                "sample_impacts": impacts
            })
            
        return results
    
    def fetch_full_story_details(self, story_id: str) -> Dict[str, Any]:
        """Fetches the full story text and associated stock impacts for a given story_id."""
        cursor = self.conn.cursor()
        
        # 1. Fetch the main story details
        # CRITICAL FIX: Column name is 'story_text', not 'text'
        story_query = "SELECT story_id, story_text, sentiment, companies_json FROM Stories WHERE story_id = ?"
        cursor.execute(story_query, (story_id,))
        story_row = cursor.fetchone()
        
        if not story_row:
            return None
            
        story_id, story_text, sentiment, companies_json = story_row
        
        # 2. Fetch all linked stock impacts
        # impacts_query = "SELECT stock_ticker, impact_direction, confidence FROM Stock_Impacts WHERE story_id = ?"
        impacts_query = """
            SELECT company_name, stock_ticker, impact_direction, confidence, impact_type 
            FROM Stock_Impacts 
            WHERE story_id = ?
        """
        cursor.execute(impacts_query, (story_id,))
        impact_rows = cursor.fetchall()
        
        # impact_details = [
        #     f"{ticker} ({direction.lower()}, Conf: {confidence:.2f})" 
        #     for ticker, direction, confidence in impact_rows
        # ]
        
        # return {
        #     "story_id": story_id,
        #     "text": story_text,  # CRITICAL FIX: Use story_text variable
        #     "sentiment": sentiment,
        #     "companies": companies_json,
        #     "impacts": ", ".join(impact_details)
        # }

        impact_details = [
            {
                "company_name": company_name,
                "stock_ticker": ticker,
                "impact_direction": direction,
                "confidence": confidence,
                "impact_type": impact_type
            }
            for company_name, ticker, direction, confidence, impact_type in impact_rows
        ]
        
        return {
            "story_id": story_id,
            "text": story_text,
            "sentiment": sentiment,
            "companies": companies_json,
            "impacts": impact_details # <-- NOW A List[Dict]
        }
    
    def fetch_all_stories_table(self) -> List[Dict[str, Any]]:
        """Fetches all rows from the Stories table and returns them as a list of dictionaries."""
        cursor = self.conn.cursor()
        
        stories_query = "SELECT * FROM Stories"
        cursor.execute(stories_query)
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Convert list of tuples to list of dictionaries
        results = [dict(zip(column_names, row)) for row in rows]
        print(f"Fetched {len(results)} rows from Stories table.")
        return results

    def fetch_all_stock_impacts_table(self) -> List[Dict[str, Any]]:
        """Fetches all rows from the Stock_Impacts table and returns them as a list of dictionaries."""
        cursor = self.conn.cursor()
        
        impacts_query = "SELECT * FROM Stock_Impacts"
        cursor.execute(impacts_query)
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Convert list of tuples to list of dictionaries
        results = [dict(zip(column_names, row)) for row in rows]
        print(f"Fetched {len(results)} rows from Stock_Impacts table.")
        return results

# Export a singleton instance
db_service = DatabaseService()