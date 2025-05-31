import React from 'react';
import { Link } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import { FaPaw, FaSignInAlt, FaUserPlus } from 'react-icons/fa';
import '../../styles/LandingPage.css';

export default function LandingPage() {
    return (
    <div className="landing-container">
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
      </div>
      
      <Container>
        <div className="hero-content">
          <div className="logo-container">
            <FaPaw className="logo-icon" />
            <span className="logo-text">PetFinderVision</span>
          </div>
          
          <h1 className="hero-title">
            Найдите своего потерянного питомца
          </h1>
          <p className="hero-subtitle">
            Используйте современные технологии для поиска и помощи в возвращении
            потерянных животных домой. Присоединяйтесь к нашему сообществу!
          </p>
          
          <div className="cta-buttons">
            <Link to="/login" className="cta-button primary-button">
              <FaSignInAlt />
              <span>Войти</span>
                </Link>
            <Link to="/register" className="cta-button secondary-button">
              <FaUserPlus />
              <span>Регистрация</span>
                </Link>
            </div>
        </div>
      </Container>
    </div>
  );
}