import { useState } from "react";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  CustomerSet,
  customerSetUpdationFormSchema,
  CustomerSetUpdationFormValues,
  customerSetType
} from "@/types/customer_set";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { updateCustomerSetMutation } from "@/store/customer_set";
import { useToast } from "@/components/ui/use-toast";
import { SubmitHandler } from "react-hook-form";

type Props = {
  customerSet: CustomerSet;
};

export const CustomerSetUpdationForm = ({ customerSet }: Props) => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const updateCustomerSet = updateCustomerSetMutation(customerSet.id);

  const form = useForm<CustomerSetUpdationFormValues>({
    resolver: zodResolver(customerSetUpdationFormSchema),
    defaultValues: customerSet,
    mode: "onChange"
  });

  const handleFormSubmit: SubmitHandler<CustomerSetUpdationFormValues> = async (values) => {
    setIsLoading(true);

    updateCustomerSet.mutate(values, {
      onSuccess: () => {
        toast({
          title: "Customer Set updated",
          description: "Customer Set has been updated successfully",
          variant: "default"
        });
      },
      onError: (error) => {
        toast({
          title: "Failed to update customer set",
          description: error.message,
          variant: "destructive"
        });
      },
      onSettled: () => {
        setIsLoading(false);
      }
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="w-full space-y-4">
        <div className="grid gap-4">
          <div className="gap-4 md:grid md:grid-cols-2">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      disabled={isLoading}
                      placeholder="Name of the customer set"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    disabled={isLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type of customer set" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {Object.values(customerSetType).map((type) => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Textarea
                    disabled={isLoading}
                    placeholder="Describe customer set"
                    rows={3}
                    {...field}
                    value={field.value ?? ""}
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
          disabled={isLoading}
        >
          Update
        </Button>
      </form>
    </Form>
  );
};
