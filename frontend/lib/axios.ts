import axios, { AxiosError, AxiosResponse } from 'axios';

const errorHandler = (error: AxiosError) => {
  return Promise.reject(error.response?.data);
};

const successHandler = <T>(response: AxiosResponse<T>) => {
  return response;
};

export const backendAxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  withCredentials: true
});

backendAxiosInstance.interceptors.response.use(successHandler, errorHandler);

