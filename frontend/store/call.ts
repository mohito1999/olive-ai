import { useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { Call, ListCall } from "@/types/call";

export const CallService = {
    listCalls: async (): Promise<ListCall[]> => {
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
    return useQuery<ListCall[]>({
        queryKey: ["calls"],
        queryFn: () => CallService.listCalls()
    });
};

export const useCallQuery = (id: string) => {
    return useQuery<Call>({
        queryKey: ["call", id],
        queryFn: () => CallService.getCall(id),
    });
};
