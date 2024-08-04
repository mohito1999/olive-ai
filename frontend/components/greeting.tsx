"use client";

import { useUser } from "@/hooks/useUser";

export const Greeting = () => {
  const { user } = useUser();
  return (
    <div>
      <h2 className="text-3xl font-bold tracking-tight mb-2">Hey there! 👋</h2>
      <p className="text-md tracking-tight">Welcome back {user?.user_metadata.display_name}</p>
    </div>
  );
};
