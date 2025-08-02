import React, { useState, useEffect, ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { User as UserType } from "@/entities/User";
import ThemeToggle from "./ThemeToggle"
import { UserAPI } from "@/entities/User"; // <- Make sure this exists as the actual API methods
import {
  Database,
  History,
  Sparkles,
  LogIn,
  LogOut,
  User as UserIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

// ✅ Add prop types
interface LayoutProps {
  children: ReactNode;
  currentPageName?: string;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const [user, setUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await UserAPI.me(); // ✅ API call
        setUser(currentUser);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    fetchUser();
  }, [location.key]);

  const handleLogin = async () => {
    await UserAPI.login();
    window.location.reload();
  };

  const handleLogout = async () => {
    await UserAPI.logout();
    setUser(null);
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background text-foreground">
        <Sidebar className="border-r border-[var(--sidebar-border)] bg-[var(--sidebar)] text-[var(--sidebar-foreground)] flex flex-col">
          <SidebarHeader className="border-b border-[var(--sidebar-border)] p-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-brand-gradient rounded-xl flex items-center justify-center shadow-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-bold text-[var(--sidebar-foreground)] text-lg">QueryMind</h2>
                <p className="text-xs text-[var(--muted-foreground)]">Natural Language SQL</p>
              </div>
            </div>
          </SidebarHeader>

          <SidebarContent className="p-1 flex-1">
            <SidebarGroup>
              <SidebarGroupLabel className="text-xs font-medium text-[var(--muted-foreground)] uppercase tracking-wider px-2 py-2">
                Navigation
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      asChild
                      className="hover:bg-[color:oklch(0.85_0.01_265)] hover:text-[var(--sidebar-foreground)] transition-all duration-200 rounded-lg mb-1 text-[var(--sidebar-foreground)]"
                    >
                      <Link
                        to={createPageUrl("interface")}
                        className="flex items-center gap-3 px-3 py-3"
                      >
                        <Sparkles className="w-5 h-5" />
                        <span className="font-medium">Query Interface</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>

                  {user && (
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        asChild
                        className="hover:bg-[color:oklch(0.85_0.01_265)] hover:text-[var(--sidebar-foreground)] transition-all duration-200 rounded-lg mb-1 text-[var(--sidebar-foreground)]"
                      >
                        <Link
                          to={createPageUrl("history")}
                          className="flex items-center gap-3 px-3 py-3"
                        >
                          <History className="w-5 h-5" />
                          <span className="font-medium">My History</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  )}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <div className="px-4 pb-2">
            <ThemeToggle />
          </div>

          <SidebarFooter className="border-t border-[var(--sidebar-border)] p-4">
            {isLoading ? (
              <div className="h-10 w-full bg-[color:oklch(0.85_0.01_265)] rounded-lg animate-pulse" />
            ) : user ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-gradient-to-tr from-cyan-500 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold">
                    {user.full_name ? (
                      user.full_name[0].toUpperCase()
                    ) : (
                      <UserIcon className="w-4 h-4" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-[var(--sidebar-foreground)] truncate text-sm">
                      {user.full_name || "User"}
                    </p>
                    <p className="text-xs text-[var(--muted-foreground)] truncate">{user.email}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  className="text-[var(--muted-foreground)] hover:text-[var(--sidebar-foreground)] hover:bg-[color:oklch(0.85_0.01_265)]"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleLogin}
                className="w-full bg-[var(--primary)] hover:bg-[var(--primary)]/90 text-[var(--primary-foreground)]"
              >
                <LogIn className="w-4 h-4 mr-2" />
                Login / Sign Up
              </Button>
            )}
          </SidebarFooter>
        </Sidebar>


        <main className="flex-1 flex flex-col bg-[var(--background)] text-[var(--foreground)]">
          <header className="bg-[var(--card)] border-b border-[var(--border)] text-[var(--foreground)] px-6 py-4 md:hidden">

            <div className="flex items-center gap-4">
              <SidebarTrigger className="hover:bg-slate-800/50 p-2 rounded-lg transition-colors duration-200 text-white" />
              <h1 className="text-xl font-bold text-white">QueryMind</h1>
            </div>
          </header>

          <div className="flex-1 overflow-auto">{children}</div>
        </main>
      </div>
    </SidebarProvider>
  );
}
