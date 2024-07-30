export type CreateTranscriber = {
    name: string;
    config: object;
};

export type Transcriber = CreateTranscriber & {
    id: string;
};
