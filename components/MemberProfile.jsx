import { UserButton, currentUser } from "@clerk/nextjs";

const MemberProfile = async () => {
  const user = await currentUser();

  if (!user) return null;

  return (
    <div className="px-4 flex items-center gap-2">
      <UserButton afterSignOutUrl="/" />
      <p>{user.emailAddresses[0].emailAddress}</p>
    </div>
  );
};
export default MemberProfile;
