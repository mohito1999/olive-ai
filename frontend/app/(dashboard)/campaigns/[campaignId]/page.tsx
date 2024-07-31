"use client";
import { useState } from "react";
import BreadCrumb from "@/components/breadcrumb";
import { CampaignForm } from "@/components/forms/campaign-form";
import { Heading } from "@/components/ui/heading";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useCampaignQuery } from "@/store/campaign";
import { useParams } from "next/navigation";
import { updateCampaignMutation } from "@/store/campaign";
import { useToast } from "@/components/ui/use-toast";
import { CampaignFormValues } from "@/types/campaign";
import { SubmitHandler } from "react-hook-form";

export default function Page() {
    const params = useParams();
    const campaignId = Array.isArray(params.campaignId) ? params.campaignId[0] : params.campaignId;
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();
    const { data: campaign } = useCampaignQuery(campaignId);
    const updateCampaign = updateCampaignMutation(campaignId);

    const handleFormSubmit: SubmitHandler<CampaignFormValues> = async (values) => {
        setIsLoading(true);
        updateCampaign.mutate(values, {
            onSuccess: () => {
                toast({
                    title: "Campaign updated",
                    description: "Campaign has been updated successfully",
                    variant: "default"
                });
            },
            onError: (error) => {
                toast({
                    title: "Failed to update campaign",
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
                        { title: campaign?.name || "", link: `/campaigns/${campaignId}` }
                    ]}
                />

                <div className="flex items-start justify-between">
                    <div>
                        <Heading title={campaign ? campaign.name : ""} description="" />
                        <code className="rounded bg-muted p-1 text-xs text-foreground">
                            {campaignId}
                        </code>
                    </div>
                    {campaign && <Badge variant="outline">{campaign.status}</Badge>}
                </div>
                <Separator />
                {campaign && (
                    <CampaignForm
                        campaign={campaign}
                        isLoading={isLoading}
                        onSubmit={handleFormSubmit}
                        buttonText="Update"
                    />
                )}
            </div>
        </ScrollArea>
    );
}
