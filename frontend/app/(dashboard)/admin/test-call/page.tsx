"use client";
import BreadCrumb from "@/components/breadcrumb";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Heading } from "@/components/ui/heading";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { zodResolver } from "@hookform/resolvers/zod";
import { SubmitHandler, useForm } from "react-hook-form";
import * as z from "zod";
import { useState } from "react";
import { requestOliveBackendWithAuth } from "@/lib/axios";

const callSchema = z.object({
    mobile_number: z.string().min(10, { message: "Please enter a valid mobile number" }),
    name: z.string().min(2, { message: "Please enter a valid name" }),
    company: z.string().min(2, { message: "Please enter a valid company name" }),
    company_product: z.string().min(2, { message: "Please enter a valid company product" }),
    prompt: z.string(),
    initial_message: z.string(),
    interrupt_sensitivity: z.string(),
    synthesizer: z.string(),
    voice: z.string().min(2, { message: "Please enter a valid voice" })
});

const defaultValues = {
    mobile_number: "",
    name: "",
    company: "",
    company_product: "",
    prompt: "",
    initial_message: "",
    interrupt_sensitivity: "low",
    synthesizer: "google",
    voice: "hi-IN-Standard-B"
};

export type CallFormValues = z.infer<typeof callSchema>;

const breadcrumbItems = [{ title: "Test call", link: "/test-call" }];

export default function Page() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);

    const form = useForm<CallFormValues>({
        resolver: zodResolver(callSchema),
        defaultValues,
        mode: "onChange"
    });
    const processForm: SubmitHandler<CallFormValues> = async (formData) => {
        setLoading(true);

        requestOliveBackendWithAuth({
            method: "POST",
            url: "/calls/outbound",
            data: formData
        })
            .then((res) => {
                toast({
                    title: "Call initiated",
                    description: "You will receive a call shortly",
                    variant: "default"
                });
                setLoading(false);
            })
            .catch((err) => {
                console.error("err ==>", err);
                toast({
                    title: "Error",
                    variant: "destructive",
                    description: err.message
                });
                setLoading(false);
            });
    };

    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
                <BreadCrumb items={breadcrumbItems} />
                <Heading
                    title="Test call"
                    description="Make a call to your mobile number to test the Olive AI agent"
                />
                <Separator />
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(processForm)} className="w-full space-y-4">
                        <div className="gap-8 md:grid md:grid-cols-2">
                            <FormField
                                control={form.control}
                                name="mobile_number"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Mobile number</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                type="tel"
                                                placeholder="9876543210"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Name</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="John"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="company"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Company name</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="Apple"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="company_product"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Product</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="iPhone 15"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="prompt"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Prompt</FormLabel>
                                        <FormControl>
                                            <Textarea
                                                disabled={loading}
                                                placeholder="..."
                                                rows={4}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="initial_message"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Initial message</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="Hi, how are you?"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="synthesizer"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Synthesizer provider</FormLabel>
                                        <FormControl>
                                            <Input disabled={loading} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="voice"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Voice</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="hi-IN-Wavenet-B"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="interrupt_sensitivity"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Interrupt Sensitivity</FormLabel>
                                        <FormControl>
                                            <Input
                                                disabled={loading}
                                                placeholder="low"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <Button
                            type="submit"
                            className="flex justify-center"
                            size={"lg"}
                            disabled={loading}
                        >
                            Start call
                        </Button>
                    </form>
                </Form>
            </div>
        </ScrollArea>
    );
}
