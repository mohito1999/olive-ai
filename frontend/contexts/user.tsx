"use client";

import { createContext, useState, useEffect } from "react";
import { createClient } from "@/utils/supabase/client";
import { User, Session } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";

type MaybeSession = Session | null;
type MaybeUser = User | null;

type UserContext = {
  user: MaybeUser;
  session: MaybeSession;
  logout: () => Promise<void>;
};

// @ts-ignore
export const UserContext = createContext<UserContext>();

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();

  const [supabase] = useState(createClient());
  const [user, setUser] = useState<MaybeUser>(null);
  const [session, setSession] = useState<MaybeSession>(null);

  const getAndSetUser = async () => {
    const {
      data: { user }
    } = await supabase.auth.getUser();
    setUser(user);
  };
  const getAndSetSession = async () => {
    const {
      data: { session }
    } = await supabase.auth.getSession();
    setSession(session);
  };

  useEffect(() => {
    getAndSetUser();
    getAndSetSession();

    supabase.auth.onAuthStateChange(() => {
      getAndSetUser();
      getAndSetSession();
    });
  }, []);

  const logout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <UserContext.Provider value={{ user, session, logout }}>
      <>{children}</>
    </UserContext.Provider>
  );
};
