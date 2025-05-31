import React, { useState, useEffect } from 'react';
import { Container, Nav, Navbar, NavDropdown, Button, Modal } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { FaPaw, FaMapMarkerAlt, FaSearch, FaUser, FaSignOutAlt, FaBrain } from 'react-icons/fa';
import '../../styles/NavbarComp.css';

export default function Header() {
  const [show, setShow] = useState(false);
  const [userAvatar, setUserAvatar] = useState(null);
  const location = useLocation();
  
  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (user?.avatar) {
      setUserAvatar(user.avatar);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('jwtToken');
    localStorage.removeItem('currentUser');
    window.location.href = '/';
  };

  return (
    <>
      <Navbar className="custom-navbar" expand="md" fixed="top">
        <Container>
          <Navbar.Brand as={Link} to="/home">
            <FaPaw size={24} style={{ color: '#FF9A9E' }} />
            PetFinderVision
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
              <NavDropdown 
                title={
                  <span>
                    <FaSearch className="me-1" />
                    Поиск питомца
                  </span>
                } 
                id="basic-nav-dropdown"
              >
                <NavDropdown.Item 
                  as={Link} 
                  to="/search-by-location"
                  className={location.pathname === '/search-by-location' ? 'active' : ''}
                >
                  <FaMapMarkerAlt className="me-2" />
                  Поиск по геопозиции
                </NavDropdown.Item>
                <NavDropdown.Item 
                  as={Link} 
                  to="/enhanced-analysis"
                  className={location.pathname === '/enhanced-analysis' ? 'active' : ''}
                >
                  <FaBrain className="me-2" />
                  AI-анализ питомца
                </NavDropdown.Item>
                <NavDropdown.Item 
                  as={Link} 
                  to="/search-by-post"
                  className={location.pathname === '/search-by-post' ? 'active' : ''}
                >
                  <FaSearch className="me-2" />
                  Поиск по объявлениям
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
            <Nav className="account-controls">
              <Nav.Link 
                as={Link} 
                to="/profile"
                className={location.pathname === '/profile' ? 'active' : ''}
              >
                {userAvatar ? (
                  <img src={userAvatar} alt="Аватар" className="user-avatar" />
                ) : (
                  <FaUser />
                )}
                <span>Личный кабинет</span>
              </Nav.Link>
              <Nav.Link onClick={handleLogout}>
                <FaSignOutAlt />
                <span>Выход</span>
              </Nav.Link>
              <Button 
                variant="link" 
                className="help-button" 
                onClick={handleShow}
                title="Помощь"
                style={{ 
                  background: 'transparent', 
                  border: 'none', 
                  padding: 0,
                  boxShadow: 'none'
                }}
              >
                <FaPaw style={{ color: '#FF9A9E', width: '20px', height: '20px' }} />
              </Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Modal show={show} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            <FaPaw className="me-2" style={{ color: '#FF9A9E' }} />
            О сервисе PetFinderVision
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
        <p>
            Наш сервис помогает владельцам домашних животных найти потерявшихся питомцев, а также помогает найти новый дом
            для бездомных животных. Мы предоставляем удобный поиск по геопозиции, фотографии или объявлениям, а также
            предлагаем возможность создания своих объявлений о потерянных или найденных животных.
          </p>
          <p>
            Мы также призываем всех наших пользователей быть ответственными владельцами и заботиться о своих питомцах.
            Помните, что животные - это наши друзья и члены семьи, и они заслуживают нашей любви и уважения.
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Закрыть
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}