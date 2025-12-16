// Home.jsx
import React from 'react';
import VesselFinder from './VesselFinder';
import BlogList from './BlogList';
import TopNav from './TopNav';
import BottomNav from './BottomNav';
import AlbumsCarousel from './AlbumCarousel';
import { useTranslation } from "react-i18next";

export default function Home() {
  const { t } = useTranslation();
  return (
    <main className="relative  text-white">
        <TopNav />
        <section className="relative">
            <VesselFinder />
            <div className="absolute top-96 z-20 w-screen">
            <BlogList />
            <AlbumsCarousel />
            <p className='p-4 text-slate-200'>{t("opvulling")}</p>
            </div>
        </section>
        <BottomNav />
    </main>
  );
}
