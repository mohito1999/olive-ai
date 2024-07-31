export type CreateCustomer = {
    organization_id: string;
    customer_set_id?: string;
    name: string;
    mobile_number: string;
    customer_metadata: object;
};

export type Customer = CreateCustomer & {
    id: string;
};
