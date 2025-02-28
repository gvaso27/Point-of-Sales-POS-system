from uuid import UUID
from abc import ABC, abstractmethod
from typing import List, Dict, Counter

from app.core.Models.campaign import Campaign, CampaignType
from app.core.Models.receipt import Receipt, ReceiptItem
from app.core.campaign import CampaignRepository
from app.core.product import ProductRepository
from app.core.receipt import ReceiptRepository
from app.core.receipt_item import ReceiptItemRepository


class ICampaign(ABC):
    @abstractmethod
    def update(self, receipt: Receipt) -> None:
        pass


class BuyNGetNCampaign(ICampaign):
    def update(self, receipt: Receipt) -> None:
        pass


class DiscountCampaign(ICampaign):

    campaignRepository: CampaignRepository

    productRepository: ProductRepository

    receiptRepository: ReceiptRepository

    receiptItemRepository: ReceiptItemRepository

    def _is_active_discount_campaign(self, campaign: Campaign) -> bool:
        return campaign.type == CampaignType.BUY_N_GET_N and campaign.is_active

    def _calculate_discounted_price(self, campaign: Campaign, receipt_item : ReceiptItem, ) -> float:
        product_price = self.productRepository.read(receipt_item.product_id).price
        return product_price * campaign.percentage * receipt_item.quantity / 100.0

    def _update_receipt_total_discount(self, campaign: Campaign, receipt: Receipt, discounted_receipt_item: ReceiptItem) -> None:
            discount_price = self._calculate_discounted_price(campaign, discounted_receipt_item)
            receipt.total_discount += discount_price
            self.receiptRepository.update(receipt)

    def _get_receipt_item_by_id(self, receipt_items : List[ReceiptItem], product_id : UUID) -> ReceiptItem | None:
        for receipt_item in receipt_items:
            if receipt_item.product_id == product_id:
                return receipt_item
        return None

    def _get_discounted_receipt_item(self, campaign : Campaign, receipt_items : List[ReceiptItem]) -> ReceiptItem | None:
        product_id = campaign.product_ids[0]
        return self._get_receipt_item_by_id(receipt_items, UUID(product_id))

    def _activate_campaign(self, campaign: Campaign, receipt: Receipt, receipt_items: List[ReceiptItem]) -> None:
        discounted_receipt_item = self._get_discounted_receipt_item(campaign, receipt_items)
        if discounted_receipt_item is not None:
            self._update_receipt_total_discount(campaign, receipt, discounted_receipt_item)

    def _activate_all_discount_campaigns(self, campaigns: List[Campaign], receipt: Receipt) -> None:
        discount_campaigns = list(filter(self._is_active_discount_campaign, campaigns))
        receipt_items = self.receiptItemRepository.read_by_receipt(receipt.id)
        for campaign in discount_campaigns:
            self._activate_campaign(campaign, receipt, receipt_items)

    def update(self, receipt: Receipt) -> None:
        campaigns = self.campaignRepository.read_all()
        if campaigns is not None:
            self._activate_all_discount_campaigns(campaigns, receipt)


class ComboCampaign(ICampaign):

    campaignRepository: CampaignRepository

    receiptItemRepository: ReceiptItemRepository

    productRepository: ProductRepository

    receiptRepository: ReceiptRepository

    def _is_active_combo_campaign(self, campaign: Campaign) -> bool:
        return campaign.type == CampaignType.COMBO and campaign.is_active

    def _get_price_for_combo_items_at_all (self, combo_product_ids: List[str]) -> float:
        price = 0.0
        for combo_product_id in combo_product_ids:
            price += self.productRepository.read(UUID(combo_product_id)).price
        return price

    def _count_combos(self, combo_product_ids: List[str], receipt_items: List[ReceiptItem]) -> int:
        count = -1
        for combo_product_id in combo_product_ids:
            for receipt_item in receipt_items:
                if str(receipt_item.product_id) == combo_product_id:
                    quantity = receipt_item.quantity
                    count = quantity if count == -1 else min(count, quantity)
        return 0 if count == -1 else count

    def _update_receipt_total_discount (self, receipt: Receipt, discount_price: float) -> None:
        receipt.total_discount += discount_price
        self.receiptRepository.update(receipt)

    def _calculate_discounted_price(self, campaign: Campaign, receipt_items: List[ReceiptItem]) -> float:
        combo_product_ids = campaign.product_ids
        combo_count = self._count_combos(combo_product_ids, receipt_items)
        return combo_count * self._get_price_for_combo_items_at_all(combo_product_ids) * campaign.percentage / 100.0

    def _activate_campaign(self, campaign: Campaign, receipt: Receipt, receipt_items: List[ReceiptItem]) -> None:
        discount_price = self._calculate_discounted_price(campaign, receipt_items)
        if discount_price > 0:
            self._update_receipt_total_discount(receipt, discount_price)

    def _activate_all_combo_campaigns(self, campaigns: List[Campaign], receipt: Receipt) -> None:
        discount_campaigns = list(filter(self._is_active_combo_campaign, campaigns))
        receipt_items = self.receiptItemRepository.read_by_receipt(receipt.id)
        for campaign in discount_campaigns:
            self._activate_campaign(campaign, receipt, receipt_items)

    def update(self, receipt: Receipt) -> None:
        campaigns = self.campaignRepository.read_all()
        if campaigns is not None:
            self._activate_all_combo_campaigns(campaigns, receipt)


class WholeReceiptDiscountCampaign(ICampaign):

    campaignRepository: CampaignRepository

    receiptRepository: ReceiptRepository

    def _is_active_whole_receipt_discount_campaign(self, campaign: Campaign) -> bool:
        return campaign.type == CampaignType.WHOLE_RECEIPT_DISCOUNT and campaign.is_active

    def _get_proper_campaign(self, receipt: Receipt) -> Campaign | None:
        campaigns = self.campaignRepository.read_all()
        proper_campaign = None
        if campaigns is not None:
            whole_receipt_discount_campaigns = list(filter(self._is_active_whole_receipt_discount_campaign, campaigns))
            for campaign in whole_receipt_discount_campaigns:
                if proper_campaign is None:
                    proper_campaign = campaign
                elif receipt.subtotal > campaign.amount_to_exceed > proper_campaign.amount_to_exceed:
                    proper_campaign = campaign
        return proper_campaign

    def update(self, receipt: Receipt) -> None:
        proper_campaign = self._get_proper_campaign(receipt)
        if proper_campaign is not None:
            receipt.total_discount += proper_campaign.percentage * receipt.subtotal / 100.0
            self.receiptRepository.update(receipt)

