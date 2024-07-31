import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { TelephonyService, CreateTelephonyService } from "@/types/telephony_service";

export const TelephonyServiceService = {
    createTelephonyService: async (payload: CreateTelephonyService): Promise<TelephonyService> => {
        const response = await requestOliveBackendWithAuth({
            url: `/telephony-services`,
            data: payload,
            method: "POST"
        });
        return response.data;
    },
    listTelephonyServices: async (): Promise<TelephonyService[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/telephony-services`, method: "GET" });
        return response.data;
    },
    getTelephonyService: async (id: string): Promise<TelephonyService> => {
        const response = await requestOliveBackendWithAuth({
            url: `/telephony-services/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateTelephonyService: async (id: string, payload: Partial<TelephonyService>): Promise<TelephonyService> => {
        const response = await requestOliveBackendWithAuth({
            url: `/telephony-services/${id}`,
            data: payload,
            method: "PATCH"
        });
        return response.data;
    }
};

export const createTelephonyServiceMutation = () => {
    return useMutation({
        mutationFn: (newTelephonyService: CreateTelephonyService) => TelephonyServiceService.createTelephonyService(newTelephonyService),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["telephony-services"] })
    });
};

export const useTelephonyServicesQuery = () => {
    return useQuery<TelephonyService[]>({
        queryKey: ["telephony-services"],
        queryFn: () => TelephonyServiceService.listTelephonyServices()
    });
};

export const useTelephonyServiceQuery = (id: string) => {
    return useQuery<TelephonyService>({
        queryKey: ["campaign", id],
        queryFn: () => TelephonyServiceService.getTelephonyService(id),
        initialData: () =>
            queryClient.getQueryData<TelephonyService[]>(["telephony-services"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["telephony-services"])?.dataUpdatedAt
    });
};

export const updateTelephonyServiceMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedTelephonyService: Partial<TelephonyService>) =>
            TelephonyServiceService.updateTelephonyService(id, updatedTelephonyService),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaign", id] })
    });
};
