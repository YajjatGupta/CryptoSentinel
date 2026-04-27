import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut, Menu, Palette, X } from "lucide-react";
import { AnimatedButton } from "@/components/ui/AnimatedButton";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/hooks/use-theme";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const navLinks = [
  { name: "Home", path: "/" },
  { name: "Features", path: "/features" },
  { name: "Pricing", path: "/pricing" },
  { name: "Contact", path: "/contact" },
];

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    toast({
      title: "Logged out successfully",
      description: "You have been logged out of your account",
    });
    navigate("/");
  };

  const renderNavLink = (link: { name: string; path: string }, mobile = false) => (
    <Link
      key={link.path}
      to={link.path}
      className={cn(
        mobile ? "text-xl font-medium" : "text-sm font-medium relative py-2",
        !mobile &&
          "after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary after:transition-all after:duration-300",
        location.pathname === link.path
          ? "text-primary after:w-full"
          : "text-foreground hover:text-primary after:w-0 hover:after:w-full"
      )}
    >
      {link.name}
    </Link>
  );

  return (
    <nav
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300 py-4 px-6 md:px-12",
        isScrolled ? "bg-background/90 backdrop-blur-lg shadow-md" : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2 z-50" aria-label="CryptoSentinel Home">
          <div className="relative h-8 w-8 overflow-hidden">
            <img src="/lg.png" alt="CryptoSentinel Logo" className="h-full w-full object-contain" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">
            Crypto<span className="text-primary">Sentinel</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center space-x-8">
          <div className="flex space-x-8 items-center">
            {navLinks.map((link) => renderNavLink(link))}
            <Link
              to="/dashboard"
              className={cn(
                "text-sm font-medium relative py-2 after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary after:transition-all after:duration-300",
                location.pathname === "/dashboard"
                  ? "text-primary after:w-full"
                  : "text-foreground hover:text-primary after:w-0 hover:after:w-full"
              )}
            >
              Dashboard
            </Link>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Change theme">
                <Palette className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme("default")} className={theme === "default" ? "bg-primary/10" : ""}>
                Dark Theme
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("light")} className={theme === "light" ? "bg-primary/10" : ""}>
                Light Theme
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="border border-primary/20 hover:bg-primary/10 text-primary">
                    {user?.name || "Account"}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate("/dashboard")}>Dashboard</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/profile")}>Profile</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/settings")}>Settings</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="outline" className="border border-primary/20 hover:bg-primary/10 text-primary">
                    Login
                  </Button>
                </Link>
                <Link to="/signup">
                  <AnimatedButton>Sign Up</AnimatedButton>
                </Link>
              </>
            )}
          </div>
        </div>

        <button
          onClick={() => setMobileMenuOpen((open) => !open)}
          className="md:hidden z-50 p-2 text-foreground focus:outline-none"
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {mobileMenuOpen ? <X className="h-6 w-6 text-primary" /> : <Menu className="h-6 w-6" />}
        </button>

        <div
          className={cn(
            "fixed inset-0 bg-background/95 backdrop-blur-lg flex flex-col justify-center items-center space-y-8 md:hidden z-40 transition-all duration-300",
            mobileMenuOpen ? "opacity-100 visible" : "opacity-0 invisible"
          )}
        >
          <div className="flex flex-col items-center space-y-6">
            {navLinks.map((link) => renderNavLink(link, true))}
            {renderNavLink({ name: "Dashboard", path: "/dashboard" }, true)}

            <div className="flex flex-col items-center space-y-2 w-full">
              <p className="text-sm text-muted-foreground">Select Theme</p>
              <div className="flex space-x-3">
                {["default", "light"].map((themeOption) => (
                  <Button
                    key={themeOption}
                    variant={theme === themeOption ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTheme(themeOption as "default" | "light")}
                  >
                    {themeOption === "default" ? "Dark" : "Light"}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-center space-y-4 w-full px-10">
            {isAuthenticated ? (
              <>
                <div className="text-center mb-4">
                  <p className="text-sm text-muted-foreground">Signed in as</p>
                  <p className="font-medium">{user?.email}</p>
                </div>
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className="w-full border border-destructive/20 hover:bg-destructive/10 text-destructive"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login" className="w-full">
                  <Button variant="outline" className="w-full border border-primary/20 hover:bg-primary/10 text-primary">
                    Login
                  </Button>
                </Link>
                <Link to="/signup" className="w-full">
                  <AnimatedButton className="w-full">Sign Up</AnimatedButton>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
