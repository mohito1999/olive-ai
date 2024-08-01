import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import {
    Campaign,
    CreateCampaign,
    ExecuteCampaignRequest,
    ExecuteCampaignResponse
} from "@/types/campaign";

export const CampaignService = {
    createCampaign: async (payload: CreateCampaign): Promise<Campaign> => {
        const response = await requestOliveBackendWithAuth({
            url: `/campaigns`,
            data: payload,
            method: "POST"
        });
        return response.data;
    },
    listCampaigns: async (): Promise<Campaign[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/campaigns`, method: "GET" });
        return response.data;
    },
    getCampaign: async (id: string): Promise<Campaign> => {
        const response = await requestOliveBackendWithAuth({
            url: `/campaigns/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateCampaign: async (id: string, payload: Partial<Campaign>): Promise<Campaign> => {
        const response = await requestOliveBackendWithAuth({
            url: `/campaigns/${id}`,
            data: payload,
            method: "PATCH"
        });
        return response.data;
    },
    deleteCampaign: async (id: string): Promise<null> => {
        const response = await requestOliveBackendWithAuth({
            url: `/campaigns/${id}`,
            method: "DELETE"
        });
        return response.data;
    },
    executeCampaign: async (
        id: string,
        payload: ExecuteCampaignRequest
    ): Promise<ExecuteCampaignResponse> => {
        const response = await requestOliveBackendWithAuth({
            url: `/campaigns/${id}/execute`,
            data: payload,
            method: "POST"
        });
        return response.data;
    }
};

export const createCampaignMutation = () => {
    return useMutation({
        mutationFn: (newCampaign: CreateCampaign) => CampaignService.createCampaign(newCampaign),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
    });
};

export const useCampaignsQuery = () => {
    return useQuery<Campaign[]>({
        queryKey: ["campaigns"],
        queryFn: () => CampaignService.listCampaigns()
    });
};

export const useCampaignQuery = (id: string) => {
    return useQuery<Campaign>({
        queryKey: ["campaign", id],
        queryFn: () => CampaignService.getCampaign(id),
        initialData: () =>
            queryClient.getQueryData<Campaign[]>(["campaigns"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["campaigns"])?.dataUpdatedAt
    });
};

export const updateCampaignMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedCampaign: Partial<Campaign>) =>
            CampaignService.updateCampaign(id, updatedCampaign),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaign", id] })
    });
};

export const deleteCampaignMutation = (id: string) => {
    return useMutation({
        mutationFn: () => CampaignService.deleteCampaign(id),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
    });
};

export const executeCampaignMutation = (id: string) => {
    return useMutation({
        mutationFn: (payload: ExecuteCampaignRequest) =>
            CampaignService.executeCampaign(id, payload),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaign", id] })
    });
};
