import React, { useState } from 'react';
import '../styles/Home.css';

const Home = ({ onGetStarted }) => {
  const [email, setEmail] = useState('');
  const [emailSubmitted, setEmailSubmitted] = useState(false);

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (email.trim()) {
      setEmailSubmitted(true);
      setEmail('');
      setTimeout(() => setEmailSubmitted(false), 3000);
    }
  };

  const features = [
    {
      icon: '📊',
      title: 'Real-time Analytics',
      description: 'Get live stock data and technical indicators updated in real-time.'
    },
    {
      icon: '🤖',
      title: 'AI Predictions',
      description: 'Machine learning models trained on historical data to predict trends.'
    },
    {
      icon: '📈',
      title: 'Interactive Charts',
      description: 'Visualize stock movements with advanced charting capabilities.'
    },
    {
      icon: '⚡',
      title: 'Fast Performance',
      description: 'Lightning-fast data processing and analysis for quick decisions.'
    }
  ];

  const steps = [
    { number: 1, title: 'Search Stock', description: 'Enter any stock ticker symbol' },
    { number: 2, title: 'View Analysis', description: 'Get technical indicators & charts' },
    { number: 3, title: 'Get Prediction', description: 'See AI-powered market prediction' },
    { number: 4, title: 'Take Action', description: 'Make informed trading decisions' }
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Stock Market Prediction with AI</h1>
          <p className="hero-subtitle">
            Harness the power of machine learning to predict stock trends and make informed investment decisions
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary" onClick={onGetStarted}>
              Get Started
            </button>
            <button className="btn btn-secondary" onClick={() => document.querySelector('.features').scrollIntoView({ behavior: 'smooth' })}>
              Learn More
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat">
              <h3>500K+</h3>
              <p>Daily Predictions</p>
            </div>
            <div className="stat">
              <h3>5000+</h3>
              <p>Stocks Tracked</p>
            </div>
            <div className="stat">
              <h3>98%</h3>
              <p>Accuracy Rate</p>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="chart-placeholder">
            <svg viewBox="0 0 200 100" preserveAspectRatio="xMidYMid meet">
              <polyline points="0,80 30,60 60,70 90,40 120,50 150,20 200,30" 
                        fill="none" stroke="#667eea" strokeWidth="2"/>
              <polyline points="0,85 30,70 60,75 90,50 120,55 150,30 200,35" 
                        fill="none" stroke="#764ba2" strokeWidth="1" opacity="0.5"/>
            </svg>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="section-header">
          <h2>Powerful Features</h2>
          <p>Everything you need for smarter stock trading</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Start Section */}
      <section className="quick-start">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Get started in just 4 simple steps</p>
        </div>
        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={index} className="step">
              <div className="step-number">{step.number}</div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
              {index < steps.length - 1 && <div className="step-arrow">→</div>}
            </div>
          ))}
        </div>
        <div className="cta-section">
          <h3>Ready to predict stock trends?</h3>
          <button className="btn btn-primary btn-large" onClick={onGetStarted}>
            Start Analyzing Stocks Now
          </button>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="newsletter">
        <div className="newsletter-content">
          <h2>Stay Updated</h2>
          <p>Get the latest predictions and market insights delivered to your inbox</p>
          <form onSubmit={handleEmailSubmit} className="email-form">
            <input
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" className="btn btn-primary">Subscribe</button>
          </form>
          {emailSubmitted && <p className="success-message">✓ Thanks for subscribing!</p>}
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <p>&copy; 2024 Stock Market Predictor. All rights reserved.</p>
        <div className="footer-links">
          <a href="#privacy">Privacy</a>
          <a href="#terms">Terms</a>
          <a href="#contact">Contact</a>
        </div>
      </footer>
    </div>
  );
};

export default Home;