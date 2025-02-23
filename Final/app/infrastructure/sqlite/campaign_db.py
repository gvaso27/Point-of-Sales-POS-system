import json
import sqlite3
from typing import List
from uuid import UUID

from app.core.campaign import Campaign


class CampaignDb:
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT,
                campaign_type TEXT,
                active INTEGER,
                conditions TEXT,
                rewards TEXT
            )
            """
            cursor.execute(create_table_query)
            connection.commit()

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            truncate_campaigns_query = """
                DELETE FROM campaigns;
            """
            cursor.execute(truncate_campaigns_query)
            connection.commit()

    def read(self, campaign_id: UUID) -> Campaign:
        select_query = """
            SELECT name, campaign_type, active, conditions, rewards, id 
            FROM campaigns 
            WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (str(campaign_id),))
            row = cursor.fetchone()
            if row:
                return Campaign(
                    name=row[0],
                    campaign_type=row[1],
                    active=bool(row[2]),
                    conditions=json.loads(row[3]),
                    rewards=json.loads(row[4]),
                    id=UUID(row[5]),
                )
            else:
                raise Exception(f"campaign with {campaign_id} does not exist")

    def add(self, campaign: Campaign) -> Campaign:
        insert_query = """
            INSERT INTO campaigns (id, name, campaign_type, active, conditions, rewards)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                insert_query,
                (
                    str(campaign.id),
                    campaign.name,
                    campaign.campaign_type,
                    campaign.active,
                    json.dumps(campaign.conditions),
                    json.dumps(campaign.rewards),
                ),
            )
            connection.commit()
            return campaign

    def find_by_name(self, name: str) -> Campaign | None:
        select_query = """
            SELECT name, campaign_type, active, conditions, rewards, id 
            FROM campaigns 
            WHERE name = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (name,))
            row = cursor.fetchone()
            if row:
                return Campaign(
                    name=row[0],
                    campaign_type=row[1],
                    active=bool(row[2]),
                    conditions=json.loads(row[3]),
                    rewards=json.loads(row[4]),
                    id=UUID(row[5]),
                )
            return None

    def read_all(self) -> List[Campaign]:
        select_query = """
            SELECT name, campaign_type, active, conditions, rewards, id 
            FROM campaigns;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                Campaign(
                    name=row[0],
                    campaign_type=row[1],
                    active=bool(row[2]),
                    conditions=json.loads(row[3]),
                    rewards=json.loads(row[4]),
                    id=UUID(row[5]),
                )
                for row in rows
            ]

    def deactivate(self, campaign_id: UUID) -> None:
        update_query = """
            UPDATE campaigns 
            SET active = 0 
            WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(update_query, (str(campaign_id),))
            if cursor.rowcount == 0:
                raise Exception(f"campaign with {campaign_id} does not exist")
            connection.commit()
