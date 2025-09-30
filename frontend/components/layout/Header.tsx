'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { ThemeToggle } from '@/components/theme-toggle'

interface NavItem {
  href: string
  label: string
}

const navItems: NavItem[] = [
  { href: '/', label: 'Home' },
  { href: '/tips', label: 'Tips' },
  { href: '/terminal', label: 'Terminal' },
  { href: '/admin', label: 'Admin' },
]

export function Header(): React.ReactElement {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = React.useState<boolean>(false)

  const isActive = (href: string): boolean => {
    return pathname === href
  }

  return (
    <header
      className="sticky top-0 z-50 w-full border-b border-border bg-card/70 backdrop-blur-sm"
      role="banner"
    >
      <div className="container-awwwards flex h-16 items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="text-xl font-bold text-foreground transition-colors hover:text-foreground/80"
          aria-label="Linux Daily Tips - Go to homepage"
        >
          Linux Daily Tips
        </Link>

        {/* Desktop Navigation */}
        <nav
          className="hidden items-center gap-6 md:flex"
          aria-label="Main navigation"
        >
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`text-sm font-medium transition-colors hover:text-foreground ${
                isActive(item.href)
                  ? 'text-foreground'
                  : 'text-muted-foreground'
              }`}
              aria-current={isActive(item.href) ? 'page' : undefined}
            >
              {item.label}
            </Link>
          ))}
          <ThemeToggle />
        </nav>

        {/* Mobile Navigation */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="text-foreground"
                aria-label="Open navigation menu"
                aria-expanded={isOpen}
              >
                {isOpen ? (
                  <X className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Menu className="h-5 w-5" aria-hidden="true" />
                )}
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetHeader>
                <SheetTitle>Navigation</SheetTitle>
              </SheetHeader>
              <nav
                className="flex flex-col gap-4 pt-6"
                aria-label="Mobile navigation"
              >
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={`text-base font-medium transition-colors hover:text-foreground ${
                      isActive(item.href)
                        ? 'text-foreground'
                        : 'text-muted-foreground'
                    }`}
                    aria-current={isActive(item.href) ? 'page' : undefined}
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}