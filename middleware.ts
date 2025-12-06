import { authMiddleware } from "@clerk/nextjs";
import { NextResponse } from "next/server";

// This example protects all routes including api/trpc routes
// Please edit this to allow other routes to be public as needed.
// See https://clerk.com/docs/references/nextjs/auth-middleware for more information about configuring your Middleware
export default authMiddleware({
  publicRoutes: [
    "/",
    "/api/vault/upload",
    "/api/vault/query",
    "/api/vault/query-stream",
  ],
  afterAuth(auth, req) {
    // If user is signed in and on the home page, redirect to /planner
    if (auth.userId && req.nextUrl.pathname === "/") {
      const plannerUrl = new URL("/planner", req.url);
      return NextResponse.redirect(plannerUrl);
    }
  },
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
