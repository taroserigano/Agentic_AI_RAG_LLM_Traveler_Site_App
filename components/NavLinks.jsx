import Link from "next/link";

const links = [
  { href: "/chat", label: "chat" },
  { href: "/tours", label: "tours" },
  { href: "/planner", label: "travel planner" },
  { href: "/planner/saved", label: "saved trips" },
  { href: "/vault", label: "knowledge vault" },
  { href: "/tours/new-tour", label: "new tour" },
];

const NavLinks = () => {
  return (
    <ul className="menu text-base-content">
      {links.map((link) => {
        return (
          <li key={link.href}>
            <Link href={link.href} className="capitalize">
              {link.label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
};
export default NavLinks;
