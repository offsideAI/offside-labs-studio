"use client";

import { Eyebrow } from "@offside/ui";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import * as React from "react";

interface NavItem {
  label: string;
  href: (slug: string) => string;
  match: (pathname: string, slug: string) => boolean;
  badge?: string;
  comingSoon?: boolean;
}

const NAV: NavItem[] = [
  {
    label: "Home",
    href: (slug) => `/${slug}`,
    match: (pathname, slug) => pathname === `/${slug}`,
  },
  {
    label: "Contacts",
    href: (slug) => `/${slug}/contacts`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/contacts`),
  },
  {
    label: "Companies",
    href: (slug) => `/${slug}/companies`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/companies`),
  },
  {
    label: "Deals",
    href: (slug) => `/${slug}/deals`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/deals`),
  },
  {
    label: "Tasks",
    href: (slug) => `/${slug}/tasks`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/tasks`),
    comingSoon: true,
    badge: "M5+",
  },
  {
    label: "Automations",
    href: (slug) => `/${slug}/automations`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/automations`),
    comingSoon: true,
    badge: "M8",
  },
];

const SECONDARY: NavItem[] = [
  {
    label: "Settings",
    href: (slug) => `/${slug}/settings`,
    match: (pathname, slug) => pathname.startsWith(`/${slug}/settings`),
  },
  {
    label: "Brand tokens",
    href: () => "/brand",
    match: (pathname) => pathname === "/brand",
  },
];

export const Sidebar = ({ workspaceName }: { workspaceName: string }) => {
  const params = useParams<{ workspace: string }>();
  const pathname = usePathname() ?? "";
  const slug = params.workspace ?? "";

  return (
    <aside
      aria-label="Primary"
      className="hidden w-60 shrink-0 border-r hairline bg-bone md:flex md:flex-col"
    >
      <div className="border-b hairline px-4 py-3">
        <Eyebrow>Workspace</Eyebrow>
        <p className="mt-1 truncate font-styrene font-bold">{workspaceName}</p>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-0.5">
          {NAV.map((item) => (
            <SidebarLink key={item.label} item={item} slug={slug} pathname={pathname} />
          ))}
        </ul>
        <hr className="my-3 hairline" />
        <ul className="space-y-0.5">
          {SECONDARY.map((item) => (
            <SidebarLink key={item.label} item={item} slug={slug} pathname={pathname} />
          ))}
        </ul>
      </nav>

      <div className="border-t hairline px-3 py-2 font-mono text-[10px] text-fg-muted">
        cmd-K · / search
      </div>
    </aside>
  );
};

const SidebarLink = ({
  item,
  slug,
  pathname,
}: {
  item: NavItem;
  slug: string;
  pathname: string;
}) => {
  const active = item.match(pathname, slug);
  const className = [
    "flex items-center justify-between rounded-sm px-3 py-1.5 text-sm transition-colors",
    active ? "bg-tan-100 text-ink" : "text-ink/80 hover:bg-tan-100/60",
    item.comingSoon ? "opacity-60" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <li>
      {item.comingSoon ? (
        <span className={className} aria-disabled>
          <span>{item.label}</span>
          {item.badge ? (
            <span className="font-mono text-[10px] text-fg-muted">{item.badge}</span>
          ) : null}
        </span>
      ) : (
        <Link href={item.href(slug)} className={className}>
          <span>{item.label}</span>
          {item.badge ? (
            <span className="font-mono text-[10px] text-fg-muted">{item.badge}</span>
          ) : null}
        </Link>
      )}
    </li>
  );
};
