import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { CustomerSet } from "@/types/customer_set";

export const CustomerSetService = {
    createCustomerSet: async (payload: FormData): Promise<CustomerSet> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customer-sets`,
            data: payload,
            method: "POST"
        });
        return response.data;
    },
    listCustomerSets: async (): Promise<CustomerSet[]> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customer-sets`,
            method: "GET"
        });
        return response.data;
    },
    getCustomerSet: async (id: string): Promise<CustomerSet> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customer-sets/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateCustomerSet: async (id: string, payload: Partial<CustomerSet>): Promise<CustomerSet> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customer-sets/${id}`,
            data: payload,
            method: "PATCH"
        });
        return response.data;
    },
    deleteCustomerSet: async (id: string): Promise<null> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customer-sets/${id}`,
            method: "DELETE"
        });
        return response.data;
    }
};

export const createCustomerSetMutation = () => {
    return useMutation({
        mutationFn: (newCustomerSet: FormData) =>
            CustomerSetService.createCustomerSet(newCustomerSet),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customer_sets"] })
    });
};

export const useCustomerSetsQuery = () => {
    return useQuery<CustomerSet[]>({
        queryKey: ["customer_sets"],
        queryFn: () => CustomerSetService.listCustomerSets()
    });
};

export const useCustomerSetQuery = (id: string) => {
    return useQuery<CustomerSet>({
        queryKey: ["customer_set", id],
        queryFn: () => CustomerSetService.getCustomerSet(id),
        initialData: () =>
            queryClient.getQueryData<CustomerSet[]>(["customer_sets"])?.find((c) => c.id === id),
        initialDataUpdatedAt: () => queryClient.getQueryState(["customer_sets"])?.dataUpdatedAt
    });
};

export const updateCustomerSetMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedCustomerSet: Partial<CustomerSet>) =>
            CustomerSetService.updateCustomerSet(id, updatedCustomerSet),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customer_set", id] })
    });
};

export const deleteCustomerSetMutation = (id: string) => {
    return useMutation({
        mutationFn: () => CustomerSetService.deleteCustomerSet(id),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                predicate: (query) =>
                    query.queryKey[0] === "campaign" ||
                    query.queryKey[0] === "campaings" ||
                    query.queryKey[0] === "customer_sets"
            });
        }
    });
};
