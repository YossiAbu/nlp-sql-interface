import React, { useState, useEffect, ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { User as UserType } from "@/entities/User";
import ThemeToggle from "./ThemeToogle"
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
      <div className="min-h-screen flex w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Sidebar className="border-r border-slate-700/50 bg-slate-900/80 backdrop-blur-xl flex flex-col">
          <SidebarHeader className="border-b border-slate-700/50 p-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-bold text-white text-lg">QueryMind</h2>
                <p className="text-xs text-slate-400">Natural Language SQL</p>
              </div>
            </div>
          </SidebarHeader>

          <SidebarContent className="p-4 flex-1">
            <SidebarGroup>
              <SidebarGroupLabel className="text-xs font-medium text-slate-400 uppercase tracking-wider px-2 py-2">
                Navigation
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      asChild
                      className="hover:bg-slate-800/50 hover:text-white transition-all duration-200 rounded-lg mb-1 text-slate-300"
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
                        className="hover:bg-slate-800/50 hover:text-white transition-all duration-200 rounded-lg mb-1 text-slate-300"
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

          <SidebarFooter className="border-t border-slate-700/50 p-4">
            {isLoading ? (
              <div className="h-10 w-full bg-slate-800/50 rounded-lg animate-pulse" />
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
                    <p className="font-semibold text-white truncate text-sm">
                      {user.full_name || "User"}
                    </p>
                    <p className="text-xs text-slate-400 truncate">{user.email}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-white hover:bg-slate-700/50"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleLogin}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                <LogIn className="w-4 h-4 mr-2" />
                Login / Sign Up
              </Button>
            )}
          </SidebarFooter>
        </Sidebar>

        <main className="flex-1 flex flex-col">
          <header className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4 md:hidden">
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
