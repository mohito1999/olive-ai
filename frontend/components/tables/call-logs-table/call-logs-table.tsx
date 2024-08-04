"use client";
import { DataTable } from "@/components/ui/data-table-new"
import { ListCall } from "@/types/call";
import { columns } from "./columns";

interface ProductsClientProps {
    data: ListCall[];
    pageCount: number;
}

export const CallLogsTable: React.FC<ProductsClientProps> = ({ data, pageCount }) => {
    return <DataTable searchKeys={["to_number", "campaign_id"]} columns={columns} pageCount={pageCount} data={data} />;
};
