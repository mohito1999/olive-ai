"use client";
import BreadCrumb from "@/components/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { useCampaignsQuery } from "@/store/campaign";
import { cn } from "@/lib/utils";
import { Plus } from "lucide-react";
import Link from "next/link";

const breadcrumbItems = [{ title: "Campaigns", link: "/campaigns" }];

export default function page() {
    const { data: campaigns, isLoading } = useCampaignsQuery();

    return (
        <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
            <BreadCrumb items={breadcrumbItems} />

            <div className="flex items-start justify-between">
                <Heading title={`Campaigns`} description="Manage campaigns" />

                <Link
                    href={"/campaigns/new"}
                    className={cn(buttonVariants({ variant: "default" }))}
                >
                    <Plus className="mr-2 h-4 w-4" /> Add New
                </Link>
            </div>
            <Separator />

            <div className="gap-4 md:grid md:grid-cols-2">
                {isLoading && <div>Loading...</div>}
                {!isLoading &&
                    campaigns &&
                    campaigns.map((campaign) => (
                        <Link href={`/campaigns/${campaign.id}`} className="">
                            <Card>
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <CardTitle>{campaign.name}</CardTitle>
                                            <span className="text-xs text-gray-500">{campaign.type}</span>
                                        </div>
                                        {campaign && (
                                            <Badge variant="outline">{campaign.status}</Badge>
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <CardDescription>{campaign.description || "(No description provided)"}</CardDescription>
                                </CardContent>
                            </Card>
                        </Link>
                    ))}
            </div>
        </div>
    );
}
