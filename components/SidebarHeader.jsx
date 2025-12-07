import { MdFlight } from "react-icons/md";
import ThemeToggle from "./ThemeToggle";
const SidebarHeader = () => {
  return (
    <div className="flex items-center mb-4 gap-4 px-4">
      <MdFlight className="w-10 h-10 text-primary" />
      <h2 className="text-xl font-extrabold text-primary mr-auto">
        TravelPlanner
      </h2>
      <ThemeToggle />
    </div>
  );
};
export default SidebarHeader;
