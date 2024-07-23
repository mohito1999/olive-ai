from .base import BaseSchema


class CampaignCustomerSetDBInputSchema(BaseSchema):
    campaign_id: str
    customer_set_id: str
    created_by: str
    updated_by: str


class CampaignCustomerSetDBSchema(CampaignCustomerSetDBInputSchema):
    id: str

