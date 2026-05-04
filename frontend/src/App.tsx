import { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import MarqueeBand from './components/MarqueeBand';
import Pipeline from './components/Pipeline';
import Metrics from './components/Metrics';
import Architecture from './components/Architecture';
import DataAssets from './components/DataAssets';
import FeatureStrip from './components/FeatureStrip';
import SearchDemo from './components/SearchDemo';
import EvaluationDashboard from './components/EvaluationDashboard';
import CTAFooter from './components/CTAFooter';
import CustomCursor from './components/CustomCursor';

export default function App() {
  return (
    <div style={{ background: '#050f1a', minHeight: '100vh', position: 'relative' }}>
      {/* Noise texture */}
      <div className="noise-overlay" />

      {/* Custom tracking cursor */}
      <CustomCursor />

      {/* Main content */}
      <div>
        <Navbar />
        <Hero />
        <MarqueeBand />
        <Pipeline />
        <Metrics />
        <SearchDemo />
        <EvaluationDashboard />
        <Architecture />
        <DataAssets />
        <FeatureStrip />
        <CTAFooter />
      </div>
    </div>
  );
}
