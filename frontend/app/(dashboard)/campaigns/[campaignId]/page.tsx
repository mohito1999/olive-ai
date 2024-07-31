"use client";
import { useState } from "react";
import { AlertModal } from "@/components/modal/alert-modal";
import BreadCrumb from "@/components/breadcrumb";
import { Button } from "@/components/ui/button";
import { CampaignForm } from "@/components/forms/campaign-form";
import { Heading } from "@/components/ui/heading";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useCampaignQuery } from "@/store/campaign";
import { useParams } from "next/navigation";
import { updateCampaignMutation, executeCampaignMutation } from "@/store/campaign";
import { useToast } from "@/components/ui/use-toast";
import {
    CampaignFormValues,
    campaignStatus,
    campaignAction,
    CampaignAction
} from "@/types/campaign";
import { SubmitHandler } from "react-hook-form";

export default function Page() {
    const params = useParams();
    const campaignId = Array.isArray(params.campaignId) ? params.campaignId[0] : params.campaignId;
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();
    const { data: campaign } = useCampaignQuery(campaignId);
    const updateCampaign = updateCampaignMutation(campaignId);
    const executeCampaign = executeCampaignMutation(campaignId);

    const [currentAction, setCurrentAction] = useState<CampaignAction | null>(null);
    const [confirmationOpen, setConfirmationOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleExecution = async () => {
        setLoading(true);

        if (!currentAction) return;

        executeCampaign.mutate(
            { action: currentAction },
            {
                onSuccess: () => {
                    toast({
                        title: "Action successful",
                        description: `Triggered action '${currentAction}' successfully`,
                        variant: "default"
                    });
                },
                onError: (error) => {
                    toast({
                        title: "Action failed",
                        description: error.message,
                        variant: "destructive"
                    });
                },
                onSettled: () => {
                    setLoading(false);
                    setConfirmationOpen(false);
                    setCurrentAction(null);
                }
            }
        );
    };

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
        <>
            <AlertModal
                isOpen={confirmationOpen}
                onClose={() => {
                    setCurrentAction(null);
                    setConfirmationOpen(false);
                }}
                onConfirm={handleExecution}
                loading={loading}
            />

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
                        <div className="flex flex-col items-end justify-end gap-2">
                            {campaign && <Badge variant="outline">{campaign.status}</Badge>}
                            {campaign && campaign.status !== campaignStatus.RUNNING && (
                                <Button
                                    type="button"
                                    className="flex justify-center bg-green-500 text-white hover:bg-green-600"
                                    size="default"
                                    disabled={isLoading}
                                    onClick={() => {
                                        setCurrentAction(campaignAction.START);
                                        setConfirmationOpen(true);
                                    }}
                                >
                                    Start
                                </Button>
                            )}
                            {campaign && campaign.status === campaignStatus.RUNNING && (
                                <Button
                                    type="button"
                                    className="flex justify-center bg-red-500 text-white hover:bg-red-600"
                                    size="default"
                                    disabled={isLoading}
                                    onClick={() => {
                                        setCurrentAction(campaignAction.STOP);
                                        setConfirmationOpen(true);
                                    }}
                                >
                                    Stop
                                </Button>
                            )}
                        </div>
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
        </>
    );
}
