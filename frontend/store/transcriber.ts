import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { Transcriber, CreateTranscriber } from "@/types/transcriber";

export const TranscriberService = {
    createTranscriber: async (payload: CreateTranscriber): Promise<Transcriber> => {
        const response = await requestOliveBackendWithAuth({
            url: `/transcribers`,
            payload,
            method: "POST"
        });
        return response.data;
    },
    listTranscribers: async (): Promise<Transcriber[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/transcribers`, method: "GET" });
        return response.data;
    },
    getTranscriber: async (id: string): Promise<Transcriber> => {
        const response = await requestOliveBackendWithAuth({
            url: `/transcribers/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateTranscriber: async (id: string, payload: Partial<Transcriber>): Promise<Transcriber> => {
        const response = await requestOliveBackendWithAuth({
            url: `/transcribers/${id}`,
            payload,
            method: "PATCH"
        });
        return response.data;
    }
};

export const createTranscriberMutation = () => {
    return useMutation({
        mutationFn: (newTranscriber: CreateTranscriber) => TranscriberService.createTranscriber(newTranscriber),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transcribers"] })
    });
};

export const useTranscribersQuery = () => {
    return useQuery<Transcriber[]>({
        queryKey: ["transcribers"],
        queryFn: () => TranscriberService.listTranscribers()
    });
};

export const useTranscriberQuery = (id: string) => {
    return useQuery<Transcriber>({
        queryKey: ["transcriber", id],
        queryFn: () => TranscriberService.getTranscriber(id),
        initialData: () =>
            queryClient.getQueryData<Transcriber[]>(["transcribers"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["transcribers"])?.dataUpdatedAt
    });
};

export const updateTranscriberMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedTranscriber: Partial<Transcriber>) =>
            TranscriberService.updateTranscriber(id, updatedTranscriber),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transcriber", id] })
    });
};
