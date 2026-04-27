import React from "react";
import { ArrowRight, LineChart, Search, Server } from "lucide-react";

const steps = [
  {
    icon: <Server className="h-5 w-5" />,
    title: "Backend fetches market data",
    description: "Flask requests recent CoinGecko price and volume history for the selected token.",
  },
  {
    icon: <Search className="h-5 w-5" />,
    title: "Model scores unusual behavior",
    description: "The detector converts raw candles into engineered features and clusters suspicious points.",
  },
  {
    icon: <LineChart className="h-5 w-5" />,
    title: "Dashboard shows reviewable events",
    description: "Charts, severity labels, and a Markdown summary give users a starting point for investigation.",
  },
];

export const Testimonials = () => {
  return (
    <section className="py-20 bg-secondary/40">
      <div className="container mx-auto px-6">
        <div className="mb-12 max-w-3xl">
          <p className="text-sm font-medium uppercase tracking-wide text-primary">Project flow</p>
          <h2 className="mt-3 text-3xl font-bold md:text-4xl">
            From market feed to anomaly report in one path.
          </h2>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step.title} className="rounded-lg border border-white/10 bg-background/70 p-6">
              <div className="mb-5 flex items-center justify-between">
                <div className="inline-flex rounded-md border border-primary/20 bg-primary/10 p-3 text-primary">
                  {step.icon}
                </div>
                {index < steps.length - 1 && <ArrowRight className="hidden h-5 w-5 text-muted-foreground md:block" />}
              </div>
              <h3 className="text-lg font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
