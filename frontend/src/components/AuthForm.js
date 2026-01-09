import React, { useState } from "react";
import "./AuthForm.css";
import { apiEndpoint } from "../config";

const AuthForm = () => {
    const [activeTab, setActiveTab] = useState("login");
    const [loginData, setLoginData] = useState({
        usernameOrEmail: "",
        password: "",
        remember: false,
    });
    const [registerData, setRegisterData] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
    });
    const [loginErrors, setLoginErrors] = useState({});
    const [registerErrors, setRegisterErrors] = useState({});
    const [focusedField, setFocusedField] = useState(null);
    const [loginMessage, setLoginMessage] = useState({ type: "", text: "" });

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password) => {
        if (password.length < 8) {
            return "Password must be at least 8 characters long";
        }
        if (!/[A-Za-z]/.test(password)) {
            return "Password must contain at least one letter";
        }
        if (!/[0-9]/.test(password)) {
            return "Password must contain at least one number";
        }
        return "";
    }

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        const errors = {};
        setLoginMessage({ type: "", text: "" });

        if (!loginData.usernameOrEmail) {
        errors.usernameOrEmail = "Username or email is required";
        }

        if (!loginData.password) {
        errors.password = "Password is required";
        }

        setLoginErrors(errors);

        if (Object.keys(errors).length === 0) {
        try {
            const response = await fetch(apiEndpoint("/api/login"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: loginData.usernameOrEmail,
                password: loginData.password,
            }),
            });

            const data = await response.json();

            if (response.ok) {
            setLoginMessage({
                type: "success",
                text: "Login successful! Redirecting...",
            });
            localStorage.setItem("token", data.token);
            localStorage.setItem("user", JSON.stringify(data.user));
            setTimeout(() => {
                window.location.reload(); // Reload to show authenticated app
            }, 500);
            } else {
            // Show specific error message from backend
            if (response.status === 401) {
                setLoginMessage({
                type: "error",
                text: "Invalid username/email or password",
                });
            } else {
                setLoginMessage({
                type: "error",
                text: data.error || "Login failed",
                });
            }
            }
        } catch (error) {
            setLoginMessage({
            type: "error",
            text: "Network error. Please try again.",
            });
        }
        }
    };

    const handleRegisterSubmit = async (e) => {
        e.preventDefault();
        const errors = {};

        if (!registerData.username) {
        errors.username = "Username is required";
        }

        if (!registerData.email) {
        errors.email = "Email is required";
        } else if (!validateEmail(registerData.email)) {
        errors.email = "Please enter a valid email";
        }

        if (!registerData.password) {
        errors.password = "Password is required";
        } else {
            const passwordError = validatePassword(registerData.password);
            if (passwordError) {
                errors.password = passwordError;
            }
        }

        if (!registerData.confirmPassword) {
        errors.confirmPassword = "Please confirm your password";
        } else if (registerData.password !== registerData.confirmPassword) {
        errors.confirmPassword = "Passwords do not match";
        }

        setRegisterErrors(errors);

        if (Object.keys(errors).length === 0) {
        try {
            const response = await fetch(apiEndpoint("/api/register"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: registerData.username,
                email: registerData.email,
                password: registerData.password,
            }),
            });

            const data = await response.json();

            if (response.status === 201) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("user", JSON.stringify(data.user));
            window.location.href = "/dashboard"; // Redirect to dashboard
            } else {
            setRegisterErrors({ email: data.error || "Registration failed" });
            }
        } catch (error) {
            setRegisterErrors({ email: "Network error. Please try again." });
        }
        }
    };

    return (
        <div className="auth-card">
        <div className="tab-nav">
            <button
            className={`tab-button ${activeTab === "login" ? "active" : ""}`}
            onClick={() => setActiveTab("login")}
            >
            Login
            </button>
            <button
            className={`tab-button ${activeTab === "register" ? "active" : ""}`}
            onClick={() => setActiveTab("register")}
            >
            Register
            </button>
        </div>

        {activeTab === "login" ? (
            <form className="auth-form" onSubmit={handleLoginSubmit}>
            <div className="form-group">
                <label htmlFor="login-username" className="form-label">
                Username or Email
                </label>
                <input
                id="login-username"
                type="text"
                className={`form-input ${focusedField === "login-username" ? "focused" : ""}`}
                placeholder="username or email"
                value={loginData.usernameOrEmail}
                onChange={(e) => {
                    setLoginData({ ...loginData, usernameOrEmail: e.target.value });
                    setLoginErrors({ ...loginErrors, usernameOrEmail: undefined });
                    setLoginMessage({ type: "", text: "" });
                }}
                onFocus={() => setFocusedField("login-username")}
                onBlur={() => setFocusedField(null)}
                />
                {loginErrors.usernameOrEmail && (
                <span className="error-text">{loginErrors.usernameOrEmail}</span>
                )}
            </div>

            <div className="form-group">
                <label htmlFor="login-password" className="form-label">
                Password
                </label>
                <input
                id="login-password"
                type="password"
                className={`form-input ${focusedField === "login-password" ? "focused" : ""}`}
                placeholder="Enter your password"
                value={loginData.password}
                onChange={(e) => {
                    setLoginData({ ...loginData, password: e.target.value });
                    setLoginErrors({ ...loginErrors, password: undefined });
                    setLoginMessage({ type: "", text: "" });
                }}
                onFocus={() => setFocusedField("login-password")}
                onBlur={() => setFocusedField(null)}
                />
                {loginErrors.password && (
                <span className="error-text">{loginErrors.password}</span>
                )}
            </div>

            <div className="checkbox-group">
                <input
                type="checkbox"
                id="remember"
                className="checkbox-input"
                checked={loginData.remember}
                onChange={(e) =>
                    setLoginData({ ...loginData, remember: e.target.checked })
                }
                />
                <label htmlFor="remember" className="checkbox-label">
                Remember me
                </label>
            </div>

            {loginMessage.text && (
                <div className={`message-box ${loginMessage.type}`}>
                {loginMessage.text}
                </div>
            )}

            <button type="submit" className="submit-button">
                Sign In
            </button>

            <div className="footer-text">
                Don't have an account?{" "}
                <a
                href="#register"
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab("register");
                }}
                className="footer-link"
                >
                Sign up
                </a>
            </div>
            </form>
        ) : (
            <form className="auth-form" onSubmit={handleRegisterSubmit}>
            <div className="form-group">
                <label htmlFor="register-username" className="form-label">
                Username
                </label>
                <input
                id="register-username"
                type="text"
                className={`form-input ${focusedField === "register-username" ? "focused" : ""}`}
                placeholder="johndoe"
                value={registerData.username}
                onChange={(e) => {
                    setRegisterData({ ...registerData, username: e.target.value });
                    setRegisterErrors({ ...registerErrors, username: undefined });
                }}
                onFocus={() => setFocusedField("register-username")}
                onBlur={() => setFocusedField(null)}
                />
                {registerErrors.username && (
                <span className="error-text">{registerErrors.username}</span>
                )}
            </div>

            <div className="form-group">
                <label htmlFor="register-email" className="form-label">
                Email Address
                </label>
                <input
                id="register-email"
                type="email"
                className={`form-input ${focusedField === "register-email" ? "focused" : ""}`}
                placeholder="you@example.com"
                value={registerData.email}
                onChange={(e) => {
                    setRegisterData({ ...registerData, email: e.target.value });
                    setRegisterErrors({ ...registerErrors, email: undefined });
                }}
                onFocus={() => setFocusedField("register-email")}
                onBlur={() => setFocusedField(null)}
                />
                {registerErrors.email && (
                <span className="error-text">{registerErrors.email}</span>
                )}
            </div>

            <div className="form-group">
                <label htmlFor="register-password" className="form-label">
                Password
                </label>
                <input
                id="register-password"
                type="password"
                className={`form-input ${focusedField === "register-password" ? "focused" : ""}`}
                placeholder="Create a password"
                value={registerData.password}
                onChange={(e) => {
                    setRegisterData({ ...registerData, password: e.target.value });
                    setRegisterErrors({ ...registerErrors, password: undefined });
                }}
                onFocus={() => setFocusedField("register-password")}
                onBlur={() => setFocusedField(null)}
                />
                {registerErrors.password && (
                <span className="error-text">{registerErrors.password}</span>
                )}
            </div>

            <div className="form-group">
                <label htmlFor="register-confirm-password" className="form-label">
                Confirm Password
                </label>
                <input
                id="register-confirm-password"
                type="password"
                className={`form-input ${focusedField === "register-confirm-password" ? "focused" : ""}`}
                placeholder="Confirm your password"
                value={registerData.confirmPassword}
                onChange={(e) => {
                    setRegisterData({
                    ...registerData,
                    confirmPassword: e.target.value,
                    });
                    setRegisterErrors({
                    ...registerErrors,
                    confirmPassword: undefined,
                    });
                }}
                onFocus={() => setFocusedField("register-confirm-password")}
                onBlur={() => setFocusedField(null)}
                />
                {registerErrors.confirmPassword && (
                <span className="error-text">
                    {registerErrors.confirmPassword}
                </span>
                )}
            </div>

            <button type="submit" className="submit-button">
                Create Account
            </button>

            <div className="footer-text">
                Already have an account?{" "}
                <a
                href="#login"
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab("login");
                }}
                className="footer-link"
                >
                Sign in
                </a>
            </div>
            </form>
        )}
        </div>
    );
};

export default AuthForm;
