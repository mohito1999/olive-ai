export type CreateAgent = {
    name: string;
    config: object;
};

export type Agent = CreateAgent & {
    id: string;
};
