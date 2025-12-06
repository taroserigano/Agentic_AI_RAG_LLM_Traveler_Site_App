import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import Providers from "./providers";
const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "TravelPlanner - AI Trip Planning",
  description:
    "Plan your perfect trip with AI-powered itinerary generation. Create detailed travel plans with top attractions, hotels, and daily schedules. Save your trips and access them anytime.",
};

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          <Providers>{children}</Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
