"use client";
import BreadCrumb from "@/components/breadcrumb";
import { CallLogsTable } from "@/components/tables/call-logs-table/call-logs-table";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { useCallsQuery } from "@/store/call";

const breadcrumbItems = [{ title: "Call Logs", link: "/call-logs" }];

export default function Page() {
    const { data: calls, isLoading } = useCallsQuery();

    return (
        <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
            <BreadCrumb items={breadcrumbItems} />

            <div className="flex items-start justify-between">
                <Heading title="Call logs" description="View call logs" />
            </div>
            <Separator />

            <CallLogsTable data={calls ?? []} pageCount={1} />
        </div>
    );
}
