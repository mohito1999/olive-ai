import { z } from "zod";
import { zodConfigJson } from "@/lib/utils";

export type CreateCampaign = {
    organization_id: string;
    name: string;
    description: string | null;
    type: string;
    status: string;
    prompt: string;
    initial_message: string;
    max_duration: number;
    max_retries: number;
    end_date: string | null;
    telephony_service_id?: string | null;
    telephony_service_config?: object | null;
    transcriber_id?: string | null;
    transcriber_config?: object | null;
    agent_id?: string | null;
    agent_config?: object | null;
    synthesizer_id?: string | null;
    synthesizer_config?: object | null;
    customer_sets: string[];
};

export type Campaign = CreateCampaign & {
    id: string;
    customer_sets: string[];
};

export const campaignFormSchema = z.object({
    name: z.string().min(2, { message: "Please enter a valid name" }),
    description: z.string().nullable(),
    type: z.string().min(2, { message: "Please enter a valid type" }),
    prompt: z.string().min(2, { message: "Please enter a valid prompt" }),
    initial_message: z.string(),
    // max_duration: z.number().int().positive(),
    // max_retries: z.number().int().positive(),
    telephony_service_id: z.string().nullable(),
    telephony_service_config: zodConfigJson,
    transcriber_id: z.string().nullable(),
    transcriber_config: zodConfigJson,
    agent_id: z.string().nullable(),
    agent_config: zodConfigJson,
    synthesizer_id: z.string().nullable(),
    synthesizer_config: zodConfigJson,
    customer_sets: z.array(z.string()),
});

export type CampaignFormValues = z.infer<typeof campaignFormSchema>;
