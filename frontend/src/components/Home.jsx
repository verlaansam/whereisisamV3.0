// Home.jsx
import React from 'react';
import VesselFinder from './VesselFinder';
import BlogList from './BlogList';
import TopNav from './TopNav';
import BottomNav from './BottomNav';
import AlbumsCarousel from './AlbumCarousel';

export default function Home() {
  return (
    <main className="relative  text-white">
        <TopNav />
        <section className="relative">
            <VesselFinder />
            <div className="absolute top-96 z-20 w-screen">
            <BlogList />
            <AlbumsCarousel />
            <p className='p-4 text-slate-200'>opvulling</p>
            </div>
        </section>
        <BottomNav />
    </main>
  );
}
