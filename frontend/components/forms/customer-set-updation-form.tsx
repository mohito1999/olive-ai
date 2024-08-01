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
import { updateCustomerSetMutation, deleteCustomerSetMutation } from "@/store/customer_set";
import { useToast } from "@/components/ui/use-toast";
import { SubmitHandler } from "react-hook-form";
import { AlertModal } from "../modal/alert-modal";
import { useRouter } from "next/navigation";

type Props = {
  customerSet: CustomerSet;
};

export const CustomerSetUpdationForm = ({ customerSet }: Props) => {
  const router = useRouter();
  const [confirmationOpen, setConfirmationOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const updateCustomerSet = updateCustomerSetMutation(customerSet.id);
  const deleteCustomerSet = deleteCustomerSetMutation(customerSet.id);

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
          title: "Customer set updated",
          description: "Customer set has been updated successfully",
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

  const handleDeleteSubmit = async () => {
    setIsLoading(true);
    deleteCustomerSet.mutate(undefined, {
      onSuccess: () => {
        toast({
          title: "Customer set deleted",
          description: "Customer set has been deleted successfully",
          variant: "default"
        });
        router.push("/customer-sets");
      },
      onError: (error) => {
        toast({
          title: "Failed to delete customer set",
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
    <>
      <AlertModal
        isOpen={confirmationOpen}
        onClose={() => setConfirmationOpen(false)}
        onConfirm={handleDeleteSubmit}
        loading={isLoading}
      />
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
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
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

          <div className="flex justify-between">
            <Button
              type="submit"
              className="flex justify-center"
              size="default"
              disabled={isLoading}
            >
              Update
            </Button>
            <Button
              type="button"
              className="flex justify-center"
              variant="destructive"
              size="default"
              disabled={isLoading}
              onClick={() => setConfirmationOpen(true)}
            >
              Delete
            </Button>
          </div>
        </form>
      </Form>
    </>
  );
};
