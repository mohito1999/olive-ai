"use client";
import BreadCrumb from "@/components/breadcrumb";
import { CustomerSetUpdationForm } from "@/components/forms/customer-set-updation-form";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CustomerTable } from "@/components/tables/customer-table/customer-table";
import { useCustomerSetQuery } from "@/store/customer_set";
import { useCustomersQuery } from "@/store/customer";
import { useParams } from "next/navigation";

export default function Page() {
    const params = useParams();
    const customerSetId = Array.isArray(params.customerSetId)
        ? params.customerSetId[0]
        : params.customerSetId;
    const { data: customerSet } = useCustomerSetQuery(customerSetId);
    const { data: customers } = useCustomersQuery(customerSetId);

    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
                <BreadCrumb
                    items={[
                        { title: "Customer sets", link: "/customer-sets" },
                        { title: customerSet?.name || "", link: `/customer-sets/${customerSetId}` }
                    ]}
                />

                <div className="flex items-start justify-between">
                    <div>
                        <Heading title={customerSet ? customerSet.name : ""} description="" />
                        <code className="rounded bg-muted p-1 text-xs text-foreground">
                            {customerSetId}
                        </code>
                    </div>
                </div>
                <Separator />
                {customerSet && <CustomerSetUpdationForm customerSet={customerSet} />}
                {customers && customers.length > 0 && <CustomerTable data={customers} pageCount={1} />}
            </div>
        </ScrollArea>
    );
}
