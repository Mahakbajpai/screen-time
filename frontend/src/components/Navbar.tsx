import SidebarIcon from "./SidebarIcon";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 h-16 flex items-center bg-slate-800 text-white shadow-lg z-50">
      <div className="flex items-center justify-between w-full px-20">
        <div className="text-2xl font-bold">Logo</div>

        <div className="flex space-x-4">
          <SidebarIcon label="Daily" to="/daily" />
          <SidebarIcon label="Weekly" to="/weekly" />
          <SidebarIcon label="Monthly" to="/monthly" />
        </div>

        <div>Theme</div>
      </div>
    </nav>
  );
}