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
  customerSetCreationFormSchema,
  CustomerSetCreationFormValues,
  customerSetType
} from "@/types/customer_set";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createCustomerSetMutation } from "@/store/customer_set";
import { useToast } from "@/components/ui/use-toast";
import { SubmitHandler } from "react-hook-form";
import { createClient } from "@/utils/supabase/client";
import { useRouter } from "next/navigation";

export const CustomerSetCreationForm = () => {
  const supabase = createClient();
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();
  const createCustomerSet = createCustomerSetMutation();

  const form = useForm<CustomerSetCreationFormValues>({
    resolver: zodResolver(customerSetCreationFormSchema),
    defaultValues: {
      name: "",
      description: "",
      type: customerSetType.FILE
    },
    mode: "onChange"
  });
  const fileRef = form.register("file");

  const getUser = async () => {
    const { data, error } = await supabase.auth.getUser();
    if (error) {
      throw error;
    }
    return data.user;
  };

  const handleFormSubmit: SubmitHandler<CustomerSetCreationFormValues> = async (values) => {
    setIsLoading(true);
    const user = await getUser();
    const organization_id = user?.user_metadata?.organization_id;
    const formData = new FormData();

    const { file, ...rest } = values;
    for (const key in rest) {
      formData.append(key, String((rest as any)[key]));
    }
    formData.append("organization_id", organization_id);
    formData.append("file", file[0]);

    createCustomerSet.mutate(formData, {
      onSuccess: () => {
        toast({
          title: "Customer Set created",
          description: `Customer Set '${values.name}' created successfully`,
          variant: "default"
        });
        router.push("/customer-sets");
      },
      onError: (error) => {
        toast({
          title: "Failed to create customer set",
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

          <FormField
            control={form.control}
            name="file"
            render={() => (
              <FormItem>
                <FormLabel>File</FormLabel>
                <FormControl>
                  <Input type="file" disabled={isLoading} {...fileRef} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button
          type="submit"
          className="flex justify-center"
          size="default"
          disabled={isLoading}
        >
          Create
        </Button>
      </form>
    </Form>
  );
};
