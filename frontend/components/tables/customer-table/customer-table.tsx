"use client";
import { DataTable } from "@/components/ui/data-table-new"
import { Customer } from "@/types/customer";
import { columns } from "./columns";

interface ProductsClientProps {
    data: Customer[];
    pageCount: number;
}

export const CustomerTable: React.FC<ProductsClientProps> = ({ data, pageCount }) => {
    return <DataTable searchKey="name" columns={columns} pageCount={pageCount} data={data} />;
};
