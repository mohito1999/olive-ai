import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import {
  MultiSelector,
  MultiSelectorContent,
  MultiSelectorInput,
  MultiSelectorItem,
  MultiSelectorList,
  MultiSelectorTrigger
} from "@/components/ui/multi-select";
import { EditableCodeBlock } from "@/components/editable-codeblock";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Campaign, campaignFormSchema, CampaignFormValues } from "@/types/campaign";
import { useAgentsQuery } from "@/store/agent";
import { useSynthesizersQuery } from "@/store/synthesizer";
import { useTranscribersQuery } from "@/store/transcriber";
import { useTelephonyServicesQuery } from "@/store/telephony_service";
import { useCustomerSetsQuery } from "@/store/customer_set";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertModal } from "../modal/alert-modal";

type props = {
  campaign?: Campaign;
  isLoading: boolean;
  onSubmit: (values: CampaignFormValues) => void;
  onDeleteSubmit?: () => void;
  buttonText?: string;
};

export const CampaignForm = ({
  campaign,
  isLoading,
  onSubmit,
  onDeleteSubmit,
  buttonText
}: props) => {
  const { data: agents } = useAgentsQuery();
  const { data: synthesizers } = useSynthesizersQuery();
  const { data: transcribers } = useTranscribersQuery();
  const { data: telephonyServices } = useTelephonyServicesQuery();
  const { data: customerSets } = useCustomerSetsQuery();
  const [confirmationOpen, setConfirmationOpen] = useState(false);

  const defaultValues = campaign
    ? Object.fromEntries(
      Object.entries(campaign).map(([key, value]) => {
        if (value === null) {
          return [key, null];
        } else if (key === "customer_sets") {
          return [key, (value as { id: string }[]).map((item) => item.id)];
        } else if (
          key === "telephony_service_config" ||
          key === "transcriber_config" ||
          key === "agent_config" ||
          key === "synthesizer_config"
        ) {
          return [key, JSON.stringify(value, null, 2)];
        }
        return [key, value];
      })
    )
    : {
      name: "",
      description: "",
      initial_message: "",
      prompt: "",
      telephony_service_id: null,
      telephony_service_config: null,
      transcriber_id: null,
      transcriber_config: null,
      agent_id: null,
      agent_config: null,
      synthesizer_id: null,
      synthesizer_config: null,
      customer_sets: []
    };

  const form = useForm<CampaignFormValues>({
    resolver: zodResolver(campaignFormSchema),
    // @ts-ignore
    values: defaultValues,
    mode: "onChange"
  });

  return (
    <>
      {onDeleteSubmit && (
        <AlertModal
          isOpen={confirmationOpen}
          onClose={() => setConfirmationOpen(false)}
          onConfirm={onDeleteSubmit}
          loading={isLoading}
        />
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="w-full space-y-4">
          <div className="grid gap-6">
            <div className="gap-6 md:grid md:grid-cols-2">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input
                        disabled={isLoading}
                        placeholder="Name of the campaign"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Input
                        disabled={isLoading}
                        placeholder="What is this campaign about?"
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
                          <SelectValue placeholder="Select type of campaign" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="OUTBOUND">OUTBOUND</SelectItem>
                        <SelectItem value="INBOUND">INBOUND</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="initial_message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Initial message</FormLabel>
                  <FormControl>
                    <Input
                      disabled={isLoading}
                      placeholder="Hello, how are you?"
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
                      disabled={isLoading}
                      placeholder="..."
                      rows={5}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="customer_sets"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Customer sets</FormLabel>
                  <MultiSelector
                    onValuesChange={field.onChange}
                    values={field.value}
                  >
                    <FormControl>
                      <MultiSelectorTrigger>
                        <MultiSelectorInput placeholder="Select customer sets for this campaign" />
                      </MultiSelectorTrigger>
                    </FormControl>
                    <MultiSelectorContent>
                      <MultiSelectorList>
                        {customerSets?.map((item) => (
                          <MultiSelectorItem
                            key={item.id}
                            value={item.id}
                          >
                            {item.name} ({item.id})
                          </MultiSelectorItem>
                        ))}
                      </MultiSelectorList>
                    </MultiSelectorContent>
                  </MultiSelector>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="advanced-options">
                <AccordionTrigger>Advanced</AccordionTrigger>
                <AccordionContent>
                  <div className="gap-6 md:grid md:grid-cols-2">
                    <div className="flex flex-col gap-4 rounded border p-4">
                      <FormField
                        control={form.control}
                        name="telephony_service_id"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Telephony service ID</FormLabel>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value ?? ""}
                              disabled={isLoading}
                            >
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="(Optional) Select Telephony Service" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {telephonyServices?.map((item) => (
                                  <SelectItem
                                    key={item.id}
                                    value={item.id}
                                  >
                                    {item.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="telephony_service_config"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>
                              Telephony service config
                            </FormLabel>
                            <FormControl>
                              <EditableCodeBlock
                                isEditable={!isLoading}
                                value={field.value}
                                onChange={field.onChange}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <div className="flex flex-col gap-4 rounded border p-4">
                      <FormField
                        control={form.control}
                        name="transcriber_id"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Transcriber ID</FormLabel>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value ?? ""}
                              disabled={isLoading}
                            >
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="(Optional) Select Transcriber" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {transcribers?.map((item) => (
                                  <SelectItem
                                    key={item.id}
                                    value={item.id}
                                  >
                                    {item.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="transcriber_config"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Transcriber config</FormLabel>
                            <FormControl>
                              <EditableCodeBlock
                                isEditable={!isLoading}
                                value={field.value}
                                onChange={field.onChange}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <div className="flex flex-col gap-4 rounded border p-4">
                      <FormField
                        control={form.control}
                        name="agent_id"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Agent ID</FormLabel>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value ?? ""}
                              disabled={isLoading}
                            >
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="(Optional) Select Agent" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {agents?.map((item) => (
                                  <SelectItem
                                    key={item.id}
                                    value={item.id}
                                  >
                                    {item.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="agent_config"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Agent config</FormLabel>
                            <FormControl>
                              <EditableCodeBlock
                                isEditable={!isLoading}
                                value={field.value}
                                onChange={field.onChange}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <div className="flex flex-col gap-4 rounded border p-4">
                      <FormField
                        control={form.control}
                        name="synthesizer_id"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Synthesizer ID</FormLabel>
                            <Select
                              onValueChange={field.onChange}
                              defaultValue={field.value ?? ""}
                              disabled={isLoading}
                            >
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="(Optional) Select Synthesizer" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {synthesizers?.map((item) => (
                                  <SelectItem
                                    key={item.id}
                                    value={item.id}
                                  >
                                    {item.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="synthesizer_config"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Synthesizer config</FormLabel>
                            <FormControl>
                              <EditableCodeBlock
                                isEditable={!isLoading}
                                value={field.value}
                                onChange={field.onChange}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          <div className="flex justify-between">
            <Button
              type="submit"
              className="flex justify-center"
              size="default"
              disabled={isLoading}
            >
              {buttonText ?? "Submit"}
            </Button>
            {onDeleteSubmit && (
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
            )}
          </div>
        </form>
      </Form>
    </>
  );
};
