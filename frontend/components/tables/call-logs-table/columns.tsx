"use client";
import { ColumnDef } from "@tanstack/react-table";
import { CellAction } from "./cell-action";
import { ListCall } from "@/types/call";
import { Checkbox } from "@/components/ui/checkbox";

export const columns: ColumnDef<ListCall>[] = [
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
        accessorKey: "id",
        header: "ID"
    },
    {
        accessorKey: "to_number",
        header: "To"
    },
    {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => (
            <code className="rounded bg-muted p-1 text-xs text-foreground">
                {row.original.status}
            </code>
        )
    },
    {
        accessorKey: "duration",
        header: "Duration",
        cell: ({ row }) => `${row.original.duration}s`
    },
    {
        accessorKey: "campaign_id",
        header: "Campaign ID"
    },
    {
        accessorKey: "customer_id",
        header: "Customer ID"
    },
    {
        accessorKey: "start_time",
        header: "Start Time"
    },
    {
        accessorKey: "end_time",
        header: "End Time"
    },
    {
        id: "actions",
        cell: ({ row }) => <CellAction data={row.original} />
    }
];
