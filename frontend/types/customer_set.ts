import { z } from "zod";

export const customerSetType = {
    FILE: "FILE"
} as const;

export type CustomerSetType = (typeof customerSetType)[keyof typeof customerSetType];

export type CustomerSet = {
    id: string;
    organization_id: string;
    name: string;
    description?: string | null;
    type: CustomerSetType;
};

const MAX_FILE_SIZE = 5242880;
const ACCEPTED_FILE_TYPES = ["text/csv"];

export const customerSetUpdationFormSchema = z.object({
    name: z.string(),
    description: z.string().nullable(),
    type: z.nativeEnum(customerSetType)
});

export const customerSetCreationFormSchema = customerSetUpdationFormSchema.extend({
    // typeof check is required to make it work in both client and server side
    file: (typeof window === "undefined" ? z.any() : z.instanceof(FileList))
        .refine((files) => files.length == 1, `Only one file is allowed.`)
        .refine((files) => files.length === 1 && files[0].size <= MAX_FILE_SIZE, `File size should be less than 5MB.`)
        .refine(
            (files) => files.length === 1 && ACCEPTED_FILE_TYPES.includes(files[0].type),
            "Only .csv files are allowed."
        )
});

export type CustomerSetUpdationFormValues = z.infer<typeof customerSetUpdationFormSchema>;
export type CustomerSetCreationFormValues = z.infer<typeof customerSetCreationFormSchema>;
