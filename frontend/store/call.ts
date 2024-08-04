import { useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { CallAction, ListCall } from "@/types/call";

export const CallService = {
    listCalls: async (limit?: number): Promise<ListCall[]> => {
        let url = `/calls`;
        if (limit) {
            url += `?limit=${limit}`;
        }
        const response = await requestOliveBackendWithAuth({ url: url, method: "GET" });
        return response.data;
    },
    getCallTranscript: async (id: string): Promise<string | null> => {
        const response = await requestOliveBackendWithAuth({
            url: `/calls/${id}/transcript`,
            method: "GET"
        });
        return response.data.transcript;
    },
    getCallActions: async (id: string): Promise<Array<CallAction>> => {
        const response = await requestOliveBackendWithAuth({
            url: `/calls/${id}/actions`,
            method: "GET"
        });
        return response.data;
    }
};

export const useCallsQuery = (limit?: number) => {
    let queryKey = ["calls"]
    if (limit) {
        queryKey.push(String(limit));
    }
    return useQuery<ListCall[]>({
        queryKey: queryKey,
        queryFn: () => CallService.listCalls(limit)
    });
};

export const useCallTranscriptQuery = (id: string) => {
    return useQuery<string | null>({
        queryKey: ["call", "transcript", id],
        queryFn: () => CallService.getCallTranscript(id),
        enabled: false
    });
};

export const useCallActionsQuery = (id: string) => {
    return useQuery<Array<CallAction>>({
        queryKey: ["call", "actions", id],
        queryFn: () => CallService.getCallActions(id),
        enabled: false
    });
};
