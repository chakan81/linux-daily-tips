import * as React from 'react'
import Link from 'next/link'
import { Github, Twitter } from 'lucide-react'

export function Footer(): React.ReactElement {
  const currentYear = new Date().getFullYear()

  return (
    <footer
      className="w-full border-t border-border bg-card/50"
      role="contentinfo"
    >
      <div className="container-awwwards py-8">
        {/* Tagline */}
        <div className="mb-6 text-center">
          <p className="text-sm text-muted-foreground">
            Master Linux command line, one tip at a time.
          </p>
        </div>

        {/* Main Footer Content */}
        <div className="flex flex-col items-center gap-6 md:flex-row md:justify-between">
          {/* Copyright */}
          <div className="text-center text-sm text-muted-foreground md:text-left">
            <p>
              &copy; {currentYear} Linux Daily Tips. All rights reserved.
            </p>
          </div>

          {/* Links */}
          <nav
            className="flex flex-wrap items-center justify-center gap-4 text-sm md:gap-6"
            aria-label="Footer navigation"
          >
            <Link
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Terms of Service
            </Link>
            <Link
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Contact
            </Link>
          </nav>

          {/* Social Links */}
          <div className="flex items-center gap-4" role="group" aria-label="Social media links">
            <Link
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground transition-colors hover:text-foreground"
              aria-label="Visit our GitHub page (opens in new tab)"
            >
              <Github className="h-5 w-5" aria-hidden="true" />
            </Link>
            <Link
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground transition-colors hover:text-foreground"
              aria-label="Visit our Twitter page (opens in new tab)"
            >
              <Twitter className="h-5 w-5" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}