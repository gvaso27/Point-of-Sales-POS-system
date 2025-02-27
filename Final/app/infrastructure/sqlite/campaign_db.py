import sqlite3
from typing import List
from uuid import UUID

from app.core.campaign import Campaign, CampaignType


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
                type TEXT,
                amount_to_exceed REAL,
                percentage REAL,
                is_active INTEGER,
                amount INTEGER,
                gift_amount INTEGER,
                gift_product_type TEXT
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
            SELECT type, amount_to_exceed, percentage, is_active, amount, gift_amount, gift_product_type 
            FROM campaigns 
            WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (str(campaign_id),))
            row = cursor.fetchone()
            if row:
                campaign_type = CampaignType(row[0])
                return Campaign(
                    type=campaign_type,
                    amount_to_exceed=row[1],
                    percentage=row[2],
                    is_active=bool(row[3]),
                    amount=row[4],
                    gift_amount=row[5],
                    gift_product_type=row[6],
                    id=campaign_id
                )
            else:
                raise Exception(f"campaign with {campaign_id} does not exist")

    def add(self, campaign: Campaign) -> Campaign:
        insert_query = """
            INSERT INTO campaigns (id, type, amount_to_exceed, percentage, is_active, amount, gift_amount, gift_product_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                insert_query,
                (
                    str(campaign.id),
                    campaign.type.value,
                    campaign.amount_to_exceed,
                    campaign.percentage,
                    int(campaign.is_active),
                    campaign.amount,
                    campaign.gift_amount,
                    campaign.gift_product_type
                ),
            )
            connection.commit()
            return campaign

    def read_all(self) -> List[Campaign]:
        select_query = """
            SELECT id, type, amount_to_exceed, percentage, is_active, amount, gift_amount, gift_product_type 
            FROM campaigns;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                Campaign(
                    id=UUID(row[0]),
                    type=CampaignType(row[1]),
                    amount_to_exceed=row[2],
                    percentage=row[3],
                    is_active=bool(row[4]),
                    amount=row[5],
                    gift_amount=row[6],
                    gift_product_type=row[7]
                )
                for row in rows
            ]

    def deactivate(self, campaign_id: UUID) -> None:
        update_query = """
            UPDATE campaigns 
            SET is_active = 0 
            WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(update_query, (str(campaign_id),))
            if cursor.rowcount == 0:
                raise Exception(f"campaign with {campaign_id} does not exist")
            connection.commit()