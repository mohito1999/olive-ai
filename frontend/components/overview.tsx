"use client";

import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCampaignsQuery } from "@/store/campaign";
import { useCustomerSetsQuery } from "@/store/customer_set";
import { useCallsQuery } from "@/store/call";
import { CallLogsTable } from "./tables/call-logs-table/call-logs-table";
import { DataTable } from "./ui/data-table-new";
import { columns } from "./tables/call-logs-table/columns";

export const Overview = () => {
  const { data: campaigns, isLoading: isLoadingCampaings } = useCampaignsQuery();
  const { data: customerSets, isLoading: isLoadingCustomerSets } = useCustomerSetsQuery();
  const { data: calls, isLoading: isLoadingCalls } = useCallsQuery(10);

  const campaignCount = campaigns?.length || 0;
  const customerSetCount = customerSets?.length || 0;

  return (
    <>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Campaings</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingCampaings ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <span className="text-2xl font-bold">{campaignCount}</span>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Customer Sets</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingCustomerSets ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <span className="text-2xl font-bold">{customerSetCount}</span>
            )}
          </CardContent>
        </Card>
      </div>
      <CardTitle className="text-sm font-medium">Last 10 calls</CardTitle>
      <Suspense>
        {isLoadingCalls ? (
          <div className="flex flex-col gap-4">
            <Skeleton className="h-8 w-full" />
            <div className="flex items-center gap-4">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-64" />
            </div>
            <div className="flex items-center gap-4">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-48" />
            </div>
          </div>
        ) : (
          <DataTable columns={columns} pageCount={1} data={calls ?? []} searchKeys={[]} showPaginationOptions={false} />
        )}
      </Suspense>
    </>
  );
};
