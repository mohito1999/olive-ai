"use client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { ListCall } from "@/types/call";
import { MoreHorizontal, FileText } from "lucide-react";
import { useState } from "react";
import { useCallTranscriptQuery, useCallActionsQuery } from "@/store/call";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface CellActionProps {
    data: ListCall;
}

export const CellAction: React.FC<CellActionProps> = ({ data }) => {
    const [openTranscript, setOpenTranscript] = useState(false);
    const [openActions, setOpenActions] = useState(false);
    const {
        data: callTranscript,
        refetch: fetchCallTranscript,
        isLoading: isTranscriptLoading
    } = useCallTranscriptQuery(data.id);
    const {
        data: callActions,
        refetch: fetchCallActions,
        isLoading: areActionsLoading
    } = useCallActionsQuery(data.id);

    const viewTranscript = () => {
        if (!callTranscript) {
            fetchCallTranscript();
        }
        setOpenTranscript(true);
    };

    const viewActions = () => {
        if (!callActions) {
            fetchCallActions();
        }
        setOpenActions(true);
    };

    return (
        <>
            <Modal
                title="Call Transcript"
                description={`Transcript for call ${data.id}`}
                isOpen={openTranscript}
                onClose={() => setOpenTranscript(false)}
            >
                <ScrollArea className="max-h-[calc(100vh-10rem)] overflow-auto">
                    {isTranscriptLoading && <p>Loading...</p>}
                    {!isTranscriptLoading && !callTranscript && <p>No transcript found</p>}
                    {!isTranscriptLoading &&
                        callTranscript &&
                        callTranscript.split("\n").map((line, index) => (
                            <p className="my-2" key={index}>
                                <span className="font-semibold">{line.split(":")[0]}</span>:
                                {line.replace(/^(BOT|HUMAN):/, "")}
                            </p>
                        ))}
                </ScrollArea>
            </Modal>
            <Modal
                title="Call Actions"
                description={`Actions for call ${data.id}`}
                isOpen={openActions}
                onClose={() => setOpenActions(false)}
            >
                <ScrollArea className="max-h-[calc(100vh-10rem)] overflow-auto">
                    {areActionsLoading && <p>Loading...</p>}
                    {!areActionsLoading && !callActions && <p>No actions found</p>}
                    {!areActionsLoading && callActions && (
                        <ul className="list-disc">
                            {callActions.map((action, index) => (
                                <li className="mb-4 ml-6" key={index}>
                                    <div className="flex items-center gap-2">
                                        <Badge variant="secondary">
                                            {action.type}
                                        </Badge>
                                        <span className="font-mono text-xs">
                                            {action.data.timestamp}
                                        </span>
                                    </div>
                                    <p className="my-2">
                                        {action.data.message}
                                    </p>
                                </li>
                            ))}
                        </ul>
                    )}
                </ScrollArea>
            </Modal>
            <DropdownMenu modal={false}>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    {/* <DropdownMenuLabel>Actions</DropdownMenuLabel> */}

                    <DropdownMenuItem onClick={viewTranscript}>
                        <FileText className="mr-2 h-4 w-4" /> View transcript
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={viewActions}>
                        <FileText className="mr-2 h-4 w-4" /> View actions
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </>
    );
};
