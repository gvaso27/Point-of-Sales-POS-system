import sqlite3
from typing import List, Optional
from uuid import UUID

from app.core.Models.campaign import Campaign, CampaignType


class CampaignDb:
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            # Create campaigns table
            create_campaigns_table_query = """
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
            cursor.execute(create_campaigns_table_query)

            # Create campaign_relations table
            create_relations_table_query = """
            CREATE TABLE IF NOT EXISTS campaign_relations (
                campaign_id TEXT,
                product_id TEXT,
                PRIMARY KEY (campaign_id, product_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
            """
            cursor.execute(create_relations_table_query)
            connection.commit()

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            # Clear both tables
            truncate_campaigns_query = """
                DELETE FROM campaigns;
            """
            truncate_relations_query = """
                DELETE FROM campaign_relations;
            """
            cursor.execute(truncate_campaigns_query)
            cursor.execute(truncate_relations_query)
            connection.commit()

    def read(self, campaign_id: UUID) -> Campaign:
        select_query = """
            SELECT type, amount_to_exceed, percentage, is_active, 
            amount, gift_amount, gift_product_type 
            FROM campaigns 
            WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (str(campaign_id),))
            row = cursor.fetchone()
            if row:
                campaign_type = CampaignType(row[0])
                campaign = Campaign(
                    type=campaign_type,
                    amount_to_exceed=row[1],
                    percentage=row[2],
                    is_active=bool(row[3]),
                    amount=row[4],
                    gift_amount=row[5],
                    gift_product_type=row[6],
                    id=campaign_id,
                )

                product_ids = self.get_campaign_product_ids(campaign_id)
                campaign.product_ids = product_ids

                return campaign
            else:
                raise Exception(f"campaign with {campaign_id} does not exist")

    def add(self, campaign: Campaign) -> Campaign:
        insert_query = """
            INSERT INTO campaigns (id, type, amount_to_exceed, percentage, is_active, 
            amount, gift_amount, gift_product_type)
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
                    campaign.gift_product_type,
                ),
            )

            if hasattr(campaign, "product_ids") and campaign.product_ids:
                self.add_campaign_product_ids(campaign.id, campaign.product_ids, cursor)

            connection.commit()
            return campaign

    def read_all(self) -> List[Campaign]:
        select_query = """
            SELECT id, type, amount_to_exceed, percentage, is_active, 
            amount, gift_amount, gift_product_type 
            FROM campaigns;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()

            campaigns = []
            for row in rows:
                campaign_id = UUID(row[0])
                campaign = Campaign(
                    id=campaign_id,
                    type=CampaignType(row[1]),
                    amount_to_exceed=row[2],
                    percentage=row[3],
                    is_active=bool(row[4]),
                    amount=row[5],
                    gift_amount=row[6],
                    gift_product_type=row[7],
                )

                product_ids = self.get_campaign_product_ids(campaign_id)
                campaign.product_ids = product_ids

                campaigns.append(campaign)

            return campaigns

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

    def add_campaign_product_ids(
        self,
        campaign_id: UUID,
        product_ids: List[str],
        cursor: Optional[sqlite3.Cursor] = None,
    ) -> None:
        insert_query = """
            INSERT INTO campaign_relations (campaign_id, product_id)
            VALUES (?, ?);
        """
        should_commit = cursor is None

        if should_commit:
            connection = sqlite3.connect(self.db_path)
            c = connection.cursor()
        else:
            assert cursor is not None
            c = cursor

        try:
            for product_id in product_ids:
                c.execute(insert_query, (str(campaign_id), product_id))

            if should_commit:
                connection.commit()
                connection.close()
        except Exception as e:
            if should_commit:
                connection.close()
            raise e

    def get_campaign_product_ids(self, campaign_id: UUID) -> List[str]:
        select_query = """
            SELECT product_id FROM campaign_relations
            WHERE campaign_id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (str(campaign_id),))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
