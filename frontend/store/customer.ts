import { useMutation, useQuery } from "@tanstack/react-query";

import { requestOliveBackendWithAuth } from "@/lib/axios";
import { queryClient } from "@/lib/query";
import { Customer, CreateCustomer } from "@/types/customer";

export const CustomerService = {
    createCustomer: async (payload: CreateCustomer): Promise<Customer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customers`,
            data: payload,
            method: "POST"
        });
        return response.data;
    },
    listCustomers: async (customerSetId: string): Promise<Customer[]> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customers?customer_set_id=${customerSetId}`,
            method: "GET"
        });
        return response.data;
    },
    getCustomer: async (id: string): Promise<Customer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customers/${id}`,
            method: "GET"
        });
        return response.data;
    },
    updateCustomer: async (id: string, payload: Partial<Customer>): Promise<Customer> => {
        const response = await requestOliveBackendWithAuth({
            url: `/customers/${id}`,
            data: payload,
            method: "PATCH"
        });
        return response.data;
    }
};

export const createCustomerMutation = () => {
    return useMutation({
        mutationFn: (newCustomer: CreateCustomer) => CustomerService.createCustomer(newCustomer),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customers"] })
    });
};

export const useCustomersQuery = (customerSetId: string) => {
    return useQuery<Customer[]>({
        queryKey: ["customers", "customerSetId", customerSetId],
        queryFn: () => CustomerService.listCustomers(customerSetId)
    });
};

export const useCustomerQuery = (customerSetId: string, id: string) => {
    return useQuery<Customer>({
        queryKey: ["customer", id],
        queryFn: () => CustomerService.getCustomer(id),
        initialData: () =>
            queryClient
                .getQueryData<Customer[]>(["customers", "customerSetId", customerSetId])
                ?.find((c) => c.id === id),
        initialDataUpdatedAt: () =>
            queryClient.getQueryState(["customers", "customerSetId", customerSetId])?.dataUpdatedAt
    });
};

export const updateCustomerMutation = (id: string) => {
    return useMutation({
        mutationFn: (updatedCustomer: Partial<Customer>) =>
            CustomerService.updateCustomer(id, updatedCustomer),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customer", id] })
    });
};
