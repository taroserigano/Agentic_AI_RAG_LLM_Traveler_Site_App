import { auth } from "@clerk/nextjs";
import { redirect } from "next/navigation";
import TravelPlanner from "@/components/TravelPlanner";

const PlannerPage = async () => {
  const { userId } = auth();
  if (!userId) {
    redirect("/");
  }

  return <TravelPlanner userId={userId} />;
};

export default PlannerPage;
