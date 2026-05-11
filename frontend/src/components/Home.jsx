// Home.jsx
import React, { Suspense, lazy } from 'react';
import TopNav from './TopNav';
import BottomNav from './BottomNav';
const VesselFinder = lazy(() => import('./VesselFinder'));
const BlogList = lazy(() => import('./BlogList'));
const AlbumsCarousel = lazy(() => import('./AlbumCarousel'));

function SectionPlaceholder({ className = "" }) {
  return (
    <div className={`rounded-3xl border border-white/10 bg-white/5 shadow-xl animate-pulse ${className}`}>
      <div className="h-64 w-full rounded-3xl bg-white/5" />
    </div>
  );
}

export default function Home() {
  return (
    <main className="relative text-white pt-14 pb-24 md:pb-12 min-w-0 overflow-x-hidden">
        <TopNav />
        <section className="w-full max-w-full mx-auto px-4 md:px-6 lg:px-8 space-y-6 md:space-y-8 min-w-0">
            <div className="grid gap-6 mt-6 md:gap-8 md:grid-cols-[1.2fr,1fr] lg:grid-cols-[1.4fr,1fr] items-start min-w-0 w-full relative">
                {/* Vessel first on all breakpoints */}
                <div className="rounded-3xl border border-white/10 bg-white/5 overflow-hidden shadow-xl min-w-0 w-full order-1 md:order-none md:col-start-1 md:row-start-1">
                    <Suspense fallback={<SectionPlaceholder className="border-0 rounded-none" />}>
                        <VesselFinder />
                    </Suspense>
                </div>

                {/* Blog moves to the right column on md+ */}
                <div className="space-y-4 min-w-0 w-full order-2 md:order-none md:col-start-2 md:row-start-1">
                    <Suspense fallback={<SectionPlaceholder className="h-full" />}>
                        <BlogList />
                    </Suspense>
                </div>

                {/* Album below vessel on md+, third on mobile */}
                <div className="min-w-0 w-full order-3 md:order-none md:col-start-1 md:row-start-2">
                    <Suspense fallback={<SectionPlaceholder />}>
                        <AlbumsCarousel />
                    </Suspense>
                </div>
            </div>
        </section>
        <BottomNav />
    </main>
  );
}
