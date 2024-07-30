import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { Agent, CreateAgent } from "@/types/agent";

export const AgentService = {
    createAgent: async (payload: CreateAgent): Promise<Agent> => {
        const response = await requestOliveBackendWithAuth({
            url: `/agents`,
            payload,
            method: "POST"
        });
        return response.data;
    },
    listAgents: async (): Promise<Agent[]> => {
        const response = await requestOliveBackendWithAuth({ url: `/agents`, method: "GET" });
        return response.data;
    },
    getAgent: async (id: string): Promise<Agent> => {
        const response = await requestOliveBackendWithAuth({
            url: `/agents/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateAgent: async (id: string, payload: Partial<Agent>): Promise<Agent> => {
        const response = await requestOliveBackendWithAuth({
            url: `/agents/${id}`,
            payload,
            method: "PATCH"
        });
        return response.data;
    }
};

export const createAgentMutation = () => {
    return useMutation({
        mutationFn: (newAgent: CreateAgent) => AgentService.createAgent(newAgent),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agents"] })
    });
};

export const useAgentsQuery = () => {
    return useQuery<Agent[]>({
        queryKey: ["agents"],
        queryFn: () => AgentService.listAgents()
    });
};

export const useAgentQuery = (id: string) => {
    return useQuery<Agent>({
        queryKey: ["agent", id],
        queryFn: () => AgentService.getAgent(id),
        initialData: () =>
            queryClient.getQueryData<Agent[]>(["agents"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["agents"])?.dataUpdatedAt
    });
};

export const updateAgentMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedAgent: Partial<Agent>) =>
            AgentService.updateAgent(id, updatedAgent),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agent", id] })
    });
};
