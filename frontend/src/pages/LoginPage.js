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
        </div>

        <AuthForm />

        <footer className="login-footer">
          <div className="footer-links">
            <a href="#warning">Not for commercial use</a>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LoginPage;
