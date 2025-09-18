// Home.jsx
import React from 'react';
import VesselFinder from './VesselFinder';
import BlogList from './BlogList';
import TopNav from './TopNav';
import BottomNav from './BottomNav';

export default function Home() {
  return (
    <main className="relative">
        <TopNav />
        <section className="relative">
            <VesselFinder />
            <div className="absolute top-96  z-20 w-screen bg-slate-50">
            <BlogList />
            </div>
        </section>
        <BottomNav />
    </main>
  );
}
