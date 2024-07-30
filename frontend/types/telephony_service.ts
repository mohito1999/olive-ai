export type CreateTelephonyService = {
    name: string;
    config: object;
};

export type TelephonyService = CreateTelephonyService & {
    id: string;
};
