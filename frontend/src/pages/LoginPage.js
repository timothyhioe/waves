import React from "react";
import AuthForm from "../components/AuthForm";
import AnimatedWaves from "../components/AnimatedWaves";
import WaveLogo from "../components/WaveLogo";
import "./LoginPage.css";

const LoginPage = () => {
  return (
    <div className="login-page">
      <AnimatedWaves />

      <div className="login-content">
        <div className="login-header">
          <WaveLogo />
          <h1 className="app-title">Waves</h1>
          <p className="app-subtitle">Your music, your way</p>
        </div>

        <AuthForm />

        <footer className="login-footer">
          <p>&copy; 2025 Waves. All rights reserved.</p>
          <div className="footer-links">
            <a href="#privacy">Privacy Policy</a>
            <span className="separator">•</span>
            <a href="#terms">Terms of Service</a>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LoginPage;
