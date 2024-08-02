"use client";
import { ColumnDef } from "@tanstack/react-table";
import { CellAction } from "./cell-action";
import { Customer } from "@/types/customer";
import { Checkbox } from "@/components/ui/checkbox";
import { EditableCodeBlock } from "@/components/editable-codeblock";

export const columns: ColumnDef<Customer>[] = [
    {
        id: "select",
        header: ({ table }) => (
            <Checkbox
                checked={table.getIsAllPageRowsSelected()}
                onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                aria-label="Select all"
            />
        ),
        cell: ({ row }) => (
            <Checkbox
                checked={row.getIsSelected()}
                onCheckedChange={(value) => row.toggleSelected(!!value)}
                aria-label="Select row"
            />
        ),
        enableSorting: false,
        enableHiding: false
    },
    {
        accessorKey: "name",
        header: "Name"
    },
    {
        accessorKey: "mobile_number",
        header: "Mobile number"
    },
    {
        accessorKey: "id",
        header: "ID"
    },
    {
        accessorKey: "customer_metadata",
        header: "Customer metadata",
        cell: ({ row }) => (
            <EditableCodeBlock
                isEditable={false}
                value={JSON.stringify(row.original.customer_metadata)}
            />
        )
    },
    {
        id: "actions",
        cell: ({ row }) => <CellAction data={row.original} />
    }
];
