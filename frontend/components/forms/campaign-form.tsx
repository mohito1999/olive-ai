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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Campaign, campaignFormSchema, CampaignFormValues } from "@/types/campaign";
import { useAgentsQuery } from "@/store/agent";
import { useSynthesizersQuery } from "@/store/synthesizer";
import { useTranscribersQuery } from "@/store/transcriber";
import { useTelephonyServicesQuery } from "@/store/telephony_service";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

type props = {
  campaign?: Campaign;
  isLoading: boolean;
  onSubmit: (values: CampaignFormValues) => void;
};

export const CampaignForm = ({ campaign, isLoading, onSubmit }: props) => {
  const { data: agents } = useAgentsQuery();
  const { data: synthesizers } = useSynthesizersQuery();
  const { data: transcribers } = useTranscribersQuery();
  const { data: telephonyServices } = useTelephonyServicesQuery();

  const defaultValues = campaign
    ? Object.fromEntries(
      Object.entries(campaign).map(([key, value]) => {
        return typeof value === "object" && value !== null
          ? [key, JSON.stringify(value)]
          : [key, value];
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
      synthesizer_config: null
    };

  const form = useForm<CampaignFormValues>({
    resolver: zodResolver(campaignFormSchema),
    defaultValues: defaultValues,
    mode: "onChange"
  });

  const getFormattedJsonValue = (value: string | null) => {
    if (!value) {
      return null;
    }

    let parsed = null;
    try {
      parsed = JSON.parse(value);
    } catch (e) {
      return typeof value === "object" ? JSON.stringify(value) : value;
    }
    return JSON.stringify(parsed, null, 2);
  };

  return (
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

          <Accordion
            type="single"
            collapsible
            className="w-full"
            defaultValue="advanced-options"
          >
            <AccordionItem value="advanced-options">
              <AccordionTrigger data-state="open">Advanced</AccordionTrigger>
              <AccordionContent>
                <div className="gap-6 md:grid md:grid-cols-2">
                  <div className="rounded border p-4">
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
                          <FormLabel>Telephony service config</FormLabel>
                          <FormControl>
                            <pre
                              className="rounded-md bg-gray-100 p-2 text-xs"
                              contentEditable={!isLoading}
                              suppressContentEditableWarning={true}
                              onBlur={(e) =>
                                field.onChange(
                                  e.currentTarget.textContent
                                )
                              }
                            >
                              {getFormattedJsonValue(field.value)}
                            </pre>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="rounded border p-4">
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
                            <pre
                              className="rounded-md bg-gray-100 p-2 text-xs"
                              contentEditable={!isLoading}
                              suppressContentEditableWarning={true}
                              onBlur={(e) =>
                                field.onChange(
                                  e.currentTarget.textContent
                                )
                              }
                            >
                              {getFormattedJsonValue(field.value)}
                            </pre>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="rounded border p-4">
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
                            <pre
                              className="rounded-md bg-gray-100 p-2 text-xs"
                              contentEditable={!isLoading}
                              suppressContentEditableWarning={true}
                              onBlur={(e) =>
                                field.onChange(
                                  e.currentTarget.textContent
                                )
                              }
                            >
                              {getFormattedJsonValue(field.value)}
                            </pre>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="rounded border p-4">
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
                            <pre
                              className="rounded-md bg-gray-100 p-2 text-xs"
                              contentEditable={!isLoading}
                              suppressContentEditableWarning={true}
                              onBlur={(e) =>
                                field.onChange(
                                  e.currentTarget.textContent
                                )
                              }
                            >
                              {getFormattedJsonValue(field.value)}
                            </pre>
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

        <Button
          type="submit"
          className="flex justify-center"
          size={"lg"}
          disabled={isLoading}
        >
          Save
        </Button>
      </form>
    </Form>
  );
};
