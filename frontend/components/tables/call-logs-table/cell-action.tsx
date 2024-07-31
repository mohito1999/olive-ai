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
import { useCallTranscriptQuery } from "@/store/call";
import { ScrollArea } from "@/components/ui/scroll-area";

interface CellActionProps {
    data: ListCall;
}

export const CellAction: React.FC<CellActionProps> = ({ data }) => {
    const [open, setOpen] = useState(false);
    const {
        data: callTranscript,
        refetch: fetchCallTranscript,
        isLoading
    } = useCallTranscriptQuery(data.id);

    const viewTranscript = () => {
        if (!callTranscript) {
            fetchCallTranscript();
        }
        setOpen(true);
    };

    return (
        <>
            <Modal
                title="Call Transcript"
                description={`Transcript for call ${data.id}`}
                isOpen={open}
                onClose={() => setOpen(false)}
            >
                <ScrollArea className="max-h-[calc(100vh-10rem)] overflow-auto">
                    {isLoading && <p>Loading...</p>}
                    {!isLoading && !callTranscript && <p>No transcript found</p>}
                    {!isLoading &&
                        callTranscript &&
                        callTranscript.split("\n").map((line, index) => (
                            <p key={index} className="my-2">
                                <span className="font-semibold">{line.split(":")[0]}</span>:
                                {line.replace(/^(BOT|HUMAN):/, '')}
                            </p>
                        ))}
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
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>

                    <DropdownMenuItem onClick={viewTranscript}>
                        <FileText className="mr-2 h-4 w-4" /> View transcript
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </>
    );
};
