import React from "react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { Button } from "@/components/ui/button";
import {
  Check,
  Shield,
  Bell,
  BarChart4,
  Brain,
  Lock,
  Server,
  Clock,
  Wallet,
  AlertTriangle,
  MessageCircle,
  ArrowRight,
} from "lucide-react";
import { Link } from "react-router-dom";

const Features = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-30 pointer-events-none" />
        <div className="absolute left-1/4 top-1/3 w-96 h-96 bg-primary/20 rounded-full blur-[100px] -z-10" />

        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Powerful Features to{" "}
              <span className="text-gradient">Secure Your Web3 Wallet</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-10">
              CryptoSentinel combines cutting-edge AI with deep on-chain
              expertise to detect and prevent digital asset fraud.
            </p>
            <Link to="/signup">
              <Button size="lg">Get Started</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {[
              {
                icon: <Brain className="h-6 w-6" />,
                title: "AI-Powered Fraud Detection",
                description:
                  "Our advanced algorithms analyze on-chain data to identify suspicious wallet activities and transactions.",
                bullets: [
                  "Detects pump & dump schemes in real-time",
                  "Identifies malicious smart contract interactions",
                  "Recognizes phishing attempts and rug pulls",
                  "Monitors for wash trading activities",
                ],
              },
              {
                icon: <Bell className="h-6 w-6" />,
                title: "Real-Time Wallet Monitoring",
                description:
                  "Get instant notifications when our AI detects suspicious activities on your connected wallet.",
                bullets: [
                  "Customizable alert thresholds",
                  "Push notifications for critical events",
                  "Email alerts for high-risk transactions",
                  "Weekly digest of all detected activities",
                ],
              },
              {
                icon: <MessageCircle className="h-6 w-6" />,
                title: "Sentiment Analysis Engine",
                description:
                  "Track how social media discussions impact token prices with our AI-powered sentiment engine.",
                bullets: [
                  "Analyzes discussions on major platforms",
                  "Monitors for coordinated social media pushes",
                  "Tracks influencer mentions and sentiment",
                  "Provides sentiment score for each token",
                ],
              },
              {
                icon: <Shield className="h-6 w-6" />,
                title: "Data Privacy & Security",
                description:
                  "Your on-chain data is processed securely with a focus on privacy and user control.",
                bullets: [
                  "Non-custodial and privacy-first",
                  "End-to-end encryption for all data",
                  "Regular smart contract security audits",
                  "No sharing of user data with third parties",
                ],
              },
            ].map((feature, index) => (
              <div key={index} className="glass-card rounded-lg p-8 hover-card">
                <div className="inline-flex p-3 rounded-lg bg-primary/10 border border-primary/20 text-primary mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground mb-6">
                  {feature.description}
                </p>
                <ul className="space-y-2">
                  {feature.bullets.map((bullet, i) => (
                    <li key={i} className="flex items-start">
                      <Check className="h-5 w-5 text-primary mr-2 flex-shrink-0" />
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Features */}
      <section className="py-16 bg-secondary/20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">
            Additional Features
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Clock className="h-5 w-5" />,
                title: "Historical Analysis",
                description:
                  "Compare current wallet patterns with historical fraud cases to improve detection accuracy.",
              },
              {
                icon: <Server className="h-5 w-5" />,
                title: "Low Latency Infrastructure",
                description:
                  "Our system processes on-chain data in milliseconds to provide timely alerts.",
              },
              {
                icon: <Lock className="h-5 w-5" />,
                title: "Multi-factor Authentication",
                description:
                  "Secure your account with additional layers of protection.",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="p-6 rounded-lg border border-white/10 bg-white/5"
              >
                <div className="flex items-center mb-4">
                  <div className="p-2 rounded-lg bg-primary/10 mr-3">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold">{feature.title}</h3>
                </div>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative">
        <div className="absolute inset-0 dot-pattern opacity-30 pointer-events-none" />
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Protect Your Investments?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of investors who trust CryptoSentinel to keep their
              portfolios safe from on-chain fraud.
            </p>
            <Link to="/signup">
              <Button size="lg" className="mr-4">
                Get Started
              </Button>
            </Link>
            <Link to="/pricing">
              <Button variant="outline" size="lg">
                View Plans
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Features;
