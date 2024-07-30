import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { Synthesizer, CreateSynthesizer } from "@/types/synthesizer";

export const SynthesizerService = {
    createSynthesizer: async (payload: CreateSynthesizer): Promise<Synthesizer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/synthesizers`,
            payload,
            method: "POST"
        });
        return response.data;
    },
    listSynthesizers: async (): Promise<Synthesizer[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/synthesizers`, method: "GET" });
        return response.data;
    },
    getSynthesizer: async (id: string): Promise<Synthesizer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/synthesizers/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateSynthesizer: async (id: string, payload: Partial<Synthesizer>): Promise<Synthesizer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/synthesizers/${id}`,
            payload,
            method: "PATCH"
        });
        return response.data;
    }
};

export const createSynthesizerMutation = () => {
    return useMutation({
        mutationFn: (newSynthesizer: CreateSynthesizer) => SynthesizerService.createSynthesizer(newSynthesizer),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["synthesizers"] })
    });
};

export const useSynthesizersQuery = () => {
    return useQuery<Synthesizer[]>({
        queryKey: ["synthesizers"],
        queryFn: () => SynthesizerService.listSynthesizers()
    });
};

export const useSynthesizerQuery = (id: string) => {
    return useQuery<Synthesizer>({
        queryKey: ["synthesizer", id],
        queryFn: () => SynthesizerService.getSynthesizer(id),
        initialData: () =>
            queryClient.getQueryData<Synthesizer[]>(["synthesizers"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["synthesizers"])?.dataUpdatedAt
    });
};

export const updateSynthesizerMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedSynthesizer: Partial<Synthesizer>) =>
            SynthesizerService.updateSynthesizer(id, updatedSynthesizer),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["synthesizer", id] })
    });
};
