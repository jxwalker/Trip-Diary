"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "🏠 Home", name: "Home" },
    { href: "/upload-new", label: "📤 Upload", name: "Upload" },
    { href: "/trips", label: "📚 My Trips", name: "My Trips" },
    { href: "/guide", label: "📖 Guide", name: "Travel Guide" },
  ];

  return (
    <nav className="bg-white shadow-md mb-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold text-blue-600">
              ✈️ Trip Diary
            </Link>
            <div className="flex space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                    pathname === item.href
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Real content from Perplexity API
          </div>
        </div>
      </div>
    </nav>
  );
}