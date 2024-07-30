import { useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { Call } from "@/types/call";

export const CallService = {
    listCalls: async (): Promise<Call[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/calls`, method: "GET" });
        return response.data;
    },
    getCall: async (id: string): Promise<Call> => {
        const response = await requestOliveBackendWithAuth({
            url: `/calls/${id}`,
            method: "GET"
        });
        return response.data;
    }
};

export const useCallsQuery = () => {
    return useQuery<Call[]>({
        queryKey: ["calls"],
        queryFn: () => CallService.listCalls()
    });
};

export const useCallQuery = (id: string) => {
    return useQuery<Call>({
        queryKey: ["call", id],
        queryFn: () => CallService.getCall(id),
        initialData: () =>
            queryClient.getQueryData<Call[]>(["calls"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["calls"])?.dataUpdatedAt
    });
};
