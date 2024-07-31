"use client";
import BreadCrumb from "@/components/breadcrumb";
import { CustomerSetCreationForm } from "@/components/forms/customer-set-creation-form";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function Page() {
    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
                <BreadCrumb
                    items={[
                        { title: "Customer Sets", link: "/customer-sets" },
                        { title: "New customer set", link: "/customer-sets/new" }
                    ]}
                />

                <div className="flex items-start justify-between">
                    <Heading title="Create customer set" description="" />
                </div>
                <Separator />
                <CustomerSetCreationForm />
            </div>
        </ScrollArea>
    );
}
