"use client";
import { useState } from "react";
import BreadCrumb from "@/components/breadcrumb";
import { CampaignForm } from "@/components/forms/campaign-form";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { createCampaignMutation } from "@/store/campaign";
import { useToast } from "@/components/ui/use-toast";
import { CreateCampaign, CampaignFormValues, campaignStatus } from "@/types/campaign";
import { SubmitHandler } from "react-hook-form";
import { createClient } from "@/utils/supabase/client";
import { useRouter } from "next/navigation";

export default function Page() {
    const supabase = createClient();
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();
    const createCampaign = createCampaignMutation();

    const getUser = async () => {
        const { data, error } = await supabase.auth.getUser();
        if (error) {
            throw error;
        }
        return data.user;
    };

    const handleFormSubmit: SubmitHandler<CampaignFormValues> = async (values) => {
        setIsLoading(true);
        const user = await getUser();
        const organization_id = user?.user_metadata?.organization_id;
        const creationPayload: CreateCampaign = {
            ...values,
            organization_id: organization_id,
            max_retries: 0,
            max_duration: 0,
            status: campaignStatus.IDLE,
            end_date: null
        };
        createCampaign.mutate(creationPayload, {
            onSuccess: () => {
                toast({
                    title: "Campaign created",
                    description: `Campaign '${values.name}' created successfully`,
                    variant: "default"
                });
                router.push("/campaigns");
            },
            onError: (error) => {
                toast({
                    title: "Failed to create campaign",
                    description: error.message,
                    variant: "destructive"
                });
            },
            onSettled: () => {
                setIsLoading(false);
            }
        });
    };

    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
                <BreadCrumb
                    items={[
                        { title: "Campaigns", link: "/campaigns" },
                        { title: "New", link: "/campaigns/new" }
                    ]}
                />

                <div className="flex items-start justify-between">
                    <Heading title="Create campaign" description="" />
                </div>
                <Separator />
                <CampaignForm
                    isLoading={isLoading}
                    onSubmit={handleFormSubmit}
                    buttonText="Create"
                />
            </div>
        </ScrollArea>
    );
}
