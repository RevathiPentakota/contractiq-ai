/**
 * Header Component
 *
 * Main navigation header with branding and quick links.
 */

interface HeaderProps {
  onNavigateToDashboard?: () => void;
  onNavigateToHistory?: () => void;
  currentPage?: "dashboard" | "history";
}

export default function Header({
  onNavigateToDashboard,
  onNavigateToHistory,
  currentPage = "dashboard",
}: HeaderProps) {
  const isActive = (page: string) =>
    currentPage === page
      ? "font-bold text-blue-600"
      : "text-gray-700 hover:text-gray-900";

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-4 sm:py-6">
          {/* Logo & Branding */}
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={onNavigateToDashboard}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700">
              <span className="text-lg font-bold text-white">⚖️</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-gray-900">ContractIQ</h1>
              <p className="text-xs text-gray-500">AI Contract Intelligence</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden gap-6 md:flex">
            <button
              onClick={onNavigateToDashboard}
              className={`text-sm font-medium transition-colors ${isActive("dashboard")}`}
            >
              Dashboard
            </button>
            <button
              onClick={onNavigateToHistory}
              className={`text-sm font-medium transition-colors ${isActive("history")}`}
            >
              Contracts
            </button>
            <a
              href="#"
              className="text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
            >
              Help
            </a>
          </nav>

          {/* User Profile */}
          <div className="flex items-center gap-4">
            <div className="hidden h-8 w-8 rounded-full bg-gray-200 sm:block" />
          </div>
        </div>
      </div>
    </header>
  );
}
