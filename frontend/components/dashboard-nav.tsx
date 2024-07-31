"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createClient } from "@/utils/supabase/client";

import { Icons } from "@/components/icons";
import { cn } from "@/lib/utils";
import { NavItem } from "@/types";
import { Dispatch, SetStateAction } from "react";
import { useSidebar } from "@/hooks/useSidebar";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";

interface DashboardNavProps {
    items: NavItem[];
    setOpen?: Dispatch<SetStateAction<boolean>>;
    isMobileNav?: boolean;
}

export function DashboardNav({ items, setOpen, isMobileNav = false }: DashboardNavProps) {
    const router = useRouter();
    const supabase = createClient();

    const path = usePathname();
    const { isMinimized } = useSidebar();

    if (!items?.length) {
        return null;
    }

    const handleLogoutClick = async () => {
        await supabase.auth.signOut();
        router.push("/login");
    };

    return (
        <nav className="grid items-start gap-2">
            <TooltipProvider>
                {items.map((item, index) => {
                    const Icon = Icons[item.icon || "arrowRight"];
                    return (
                        item.href && (
                            <Tooltip key={index}>
                                <TooltipTrigger asChild>
                                    <Link
                                        href={item.disabled ? "/" : item.href}
                                        className={cn(
                                            "flex items-center gap-2 overflow-hidden rounded-md py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground",
                                            item.href != "/" && path.startsWith(item.href) ? "bg-accent" : "transparent",
                                            item.disabled && "cursor-not-allowed opacity-80"
                                        )}
                                        onClick={() => {
                                            if (setOpen) setOpen(false);
                                        }}
                                    >
                                        <Icon className={`ml-3 size-5`} />

                                        {isMobileNav || (!isMinimized && !isMobileNav) ? (
                                            <span className="mr-2 truncate">{item.title}</span>
                                        ) : (
                                            ""
                                        )}
                                    </Link>
                                </TooltipTrigger>
                                <TooltipContent
                                    align="center"
                                    side="right"
                                    sideOffset={8}
                                    className={!isMinimized ? "hidden" : "inline-block"}
                                >
                                    {item.title}
                                </TooltipContent>
                            </Tooltip>
                        )
                    );
                })}

                <span className="mt-auto w-full border-t" />

                <Tooltip key="logout">
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            className="text-left flex items-center gap-2 overflow-hidden rounded-md py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground"
                            onClick={handleLogoutClick}
                        >
                            <Icons.login className={`ml-3 size-5`} />

                            {isMobileNav || (!isMinimized && !isMobileNav) ? (
                                <span className="mr-2 truncate">Logout</span>
                            ) : (
                                ""
                            )}
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent
                        align="center"
                        side="right"
                        sideOffset={8}
                        className={!isMinimized ? "hidden" : "inline-block"}
                    >
                        Logout
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </nav>
    );
}
