export type CreateSynthesizer = {
    name: string;
    config: object;
};

export type Synthesizer = CreateSynthesizer & {
    id: string;
};
