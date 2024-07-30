import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { z } from "zod";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export const zodConfigJson = z
    .string()
    .nullable()
    .transform((str, ctx) => {
        if (!str) {
            return str;
        }
        try {
            return JSON.parse(str);
        } catch (e) {
            ctx.addIssue({ code: "custom", message: "Invalid JSON" });
            return z.NEVER;
        }
    });
