import axios, { AxiosError, AxiosResponse } from "axios";
import { createClient } from "@/utils/supabase/client";

const errorHandler = (error: AxiosError) => {
  return Promise.reject(error.response?.data);
};

const successHandler = <T>(response: AxiosResponse<T>) => {
  return response;
};

export const oliveBackendAxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  withCredentials: true
});

oliveBackendAxiosInstance.interceptors.response.use(successHandler, errorHandler);

export const requestOliveBackendWithAuth = async ({ ...options }) => {
  const supabase = createClient();
  const { data } = await supabase.auth.getSession();
  const token = data?.session?.access_token || "";

  oliveBackendAxiosInstance.defaults.headers.common.Authorization = `Bearer ${token}`;
  return oliveBackendAxiosInstance(options);
};

export default requestOliveBackendWithAuth;
