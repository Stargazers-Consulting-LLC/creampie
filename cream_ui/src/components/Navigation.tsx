/**
 * Main navigation component using shadcn/ui navigation menu.
 * Provides responsive navigation with dropdown menus and mobile support.
 *
 * SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
 * SPDX-License-Identifier: MIT
 */

import * as React from 'react';
import { Link } from 'react-router-dom';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu';
import { cn } from '@/lib/utils';

export function Navigation() {
  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4">
        <NavigationMenu>
          <NavigationMenuList>
            {/* Logo */}
            <NavigationMenuItem>
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-2xl font-bold text-indigo-600">Cream</span>
              </Link>
            </NavigationMenuItem>

            {/* Main Navigation */}
            <NavigationMenuItem>
              <Link to="/" className={navigationMenuTriggerStyle()}>
                Home
              </Link>
            </NavigationMenuItem>

            {/* Stock Tracking Navigation */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>Stock Tracking</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[500px] lg:grid-cols-2">
                  <li className="row-span-3">
                    <NavigationMenuLink asChild>
                      <Link
                        to="/stock-request"
                        className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-green-500 to-green-600 p-6 no-underline outline-none focus:shadow-md"
                      >
                        <div className="mb-2 mt-4 text-lg font-medium text-white">
                          Request Stock Tracking
                        </div>
                        <p className="text-sm leading-tight text-white/90">
                          Submit a request to track a stock symbol and receive updates.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                  <li>
                    <NavigationMenuLink asChild>
                      <Link
                        to="/admin/tracked-stocks"
                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                      >
                        <div className="text-sm font-medium leading-none">
                          Manage Tracked Stocks
                        </div>
                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                          View and manage all tracked stocks (Admin only).
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                  <li>
                    <NavigationMenuLink asChild>
                      <Link
                        to="/dashboard"
                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                      >
                        <div className="text-sm font-medium leading-none">Dashboard</div>
                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                          View your personal dashboard and tracked stocks.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <NavigationMenuTrigger>Learn</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[500px] lg:grid-cols-2">
                  <li className="row-span-3">
                    <NavigationMenuLink asChild>
                      <Link
                        to="/docs"
                        className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-indigo-500 to-indigo-600 p-6 no-underline outline-none focus:shadow-md"
                      >
                        <div className="mb-2 mt-4 text-lg font-medium text-white">
                          Documentation
                        </div>
                        <p className="text-sm leading-tight text-white/90">
                          Learn about our tools and how to use them effectively.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                  <li>
                    <NavigationMenuLink asChild>
                      <Link
                        to="/docs/quickstart"
                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                      >
                        <div className="text-sm font-medium leading-none">Quick Start</div>
                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                          Get started with our basic tools and features.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                  <li>
                    <NavigationMenuLink asChild>
                      <Link
                        to="/docs/advanced"
                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                      >
                        <div className="text-sm font-medium leading-none">Advanced Topics</div>
                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                          Deep dive into advanced features and concepts.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <Link to="/about" className={navigationMenuTriggerStyle()}>
                About
              </Link>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>

        {/* Auth Buttons */}
        <div className="ml-auto flex items-center space-x-4">
          <Link
            to="/auth/login"
            className={cn(navigationMenuTriggerStyle(), 'bg-transparent hover:bg-accent')}
          >
            Login
          </Link>
          <Link
            to="/auth/signup"
            className={cn(
              navigationMenuTriggerStyle(),
              'bg-indigo-600 text-white hover:bg-indigo-700'
            )}
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
}
