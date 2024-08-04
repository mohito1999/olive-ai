"use client";
import BreadCrumb from "@/components/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useCustomerSetsQuery } from "@/store/customer_set";
import { cn } from "@/lib/utils";
import { Plus } from "lucide-react";
import Link from "next/link";

export default function Page() {
    const { data: customerSets, isLoading } = useCustomerSetsQuery();

    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
                <BreadCrumb items={[{ title: "Customer sets", link: "/customer_sets" }]} />

                <div className="flex items-start justify-between">
                    <Heading title="Customer sets" description="Manage customer sets" />

                    <Link
                        href={"/customer-sets/new"}
                        className={cn(buttonVariants({ variant: "default" }))}
                    >
                        <Plus className="mr-2 h-4 w-4" /> Add New
                    </Link>
                </div>
                <Separator />

                <div className="flex flex-col gap-4 md:grid md:grid-cols-2">
                    {isLoading && <div>Loading...</div>}
                    {!isLoading &&
                        customerSets &&
                        customerSets.map((customer_set) => (
                            <Link href={`/customer-sets/${customer_set.id}`} key={customer_set.id}>
                                <Card>
                                    <CardHeader>
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <CardTitle>{customer_set.name}</CardTitle>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <CardDescription>
                                            {customer_set.description ||
                                                "(No description provided)"}
                                        </CardDescription>
                                    </CardContent>
                                </Card>
                            </Link>
                        ))}
                </div>
                {!isLoading && customerSets && customerSets.length === 0 && (
                    <p className="text-center text-sm text-muted-foreground">
                        No customer sets found
                    </p>
                )}
            </div>
        </ScrollArea>
    );
}
