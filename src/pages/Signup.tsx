import React from "react";
import { Link } from "react-router-dom";
import AuthForm from "@/components/auth/AuthForm";

const Signup = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="py-4 px-6 border-b border-white/10">
        <div className="max-w-7xl mx-auto flex justify-center md:justify-between items-center">
          <Link to="/" className="flex items-center space-x-2">
            <div className="relative h-8 w-8 overflow-hidden">
              <img src="/lg.png" alt="CryptoSentinel Logo" className="h-full w-full object-contain" />
            </div>
            <span className="text-xl font-bold">
              Crypto<span className="text-primary">Sentinel</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center space-x-4">
            <Link
              to="/login"
              className="text-sm text-muted-foreground hover:text-primary"
            >
              Already have an account?
            </Link>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <AuthForm defaultMode="signup" />
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 px-6 border-t border-white/10 text-center">
        <p className="text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} CryptoSentinel. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default Signup;
