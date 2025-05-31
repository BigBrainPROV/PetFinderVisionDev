import React from 'react';
import { Card, Row, Col, Badge, ProgressBar, Alert } from 'react-bootstrap';
import { FaBrain, FaChartLine, FaEye, FaPaw, FaStar } from 'react-icons/fa';

const PetMetricsDisplay = ({ advertisement }) => {
  if (!advertisement) return null;

  const formatConfidence = (confidence) => {
    return `${Math.round((confidence || 0) * 100)}%`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'danger';
  };

  const renderAIMetrics = () => {
    const hasMetrics = advertisement.fluffiness_score !== null || 
                      advertisement.symmetry_score !== null || 
                      advertisement.pattern_complexity !== null ||
                      advertisement.body_proportions !== null ||
                      advertisement.color_diversity !== null;

    if (!hasMetrics) return null;

    return (
      <Card className="mb-4">
        <Card.Header>
          <h5><FaChartLine className="me-2" />AI-метрики питомца</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              {advertisement.fluffiness_score !== null && (
                <div className="metric-item mb-3">
                  <label>Пушистость</label>
                  <ProgressBar 
                    now={advertisement.fluffiness_score * 100} 
                    label={`${Math.round(advertisement.fluffiness_score * 100)}%`}
                    variant={advertisement.fluffiness_score > 0.7 ? 'success' : 
                            advertisement.fluffiness_score > 0.4 ? 'warning' : 'info'}
                  />
                  <small className="text-muted">
                    {advertisement.fluffiness_score > 0.7 ? 'Очень пушистый' : 
                     advertisement.fluffiness_score > 0.4 ? 'Умеренно пушистый' : 'Гладкошерстный'}
                  </small>
                </div>
              )}
              
              {advertisement.symmetry_score !== null && (
                <div className="metric-item mb-3">
                  <label>Симметрия мордочки</label>
                  <ProgressBar 
                    now={advertisement.symmetry_score * 100} 
                    label={`${Math.round(advertisement.symmetry_score * 100)}%`}
                    variant={advertisement.symmetry_score > 0.8 ? 'success' : 'warning'}
                  />
                  <small className="text-muted">
                    {advertisement.symmetry_score > 0.8 ? 'Очень симметричная' : 'Умеренно симметричная'}
                  </small>
                </div>
              )}
            </Col>
            
            <Col md={6}>
              {advertisement.pattern_complexity !== null && (
                <div className="metric-item mb-3">
                  <label>Сложность узора</label>
                  <div className="d-flex align-items-center">
                    <Badge bg={advertisement.pattern_complexity > 20 ? 'success' : 
                              advertisement.pattern_complexity > 10 ? 'warning' : 'secondary'}>
                      {Math.round(advertisement.pattern_complexity)}
                    </Badge>
                    <span className="ms-2">
                      {advertisement.pattern_complexity > 20 ? 'Сложный узор' : 
                       advertisement.pattern_complexity > 10 ? 'Умеренный узор' : 'Простой окрас'}
                    </span>
                  </div>
                </div>
              )}
              
              {advertisement.color_diversity !== null && (
                <div className="metric-item mb-3">
                  <label>Разнообразие цветов</label>
                  <div className="d-flex align-items-center">
                    <Badge bg={advertisement.color_diversity > 3 ? 'success' : 
                              advertisement.color_diversity > 2 ? 'warning' : 'secondary'}>
                      {advertisement.color_diversity}
                    </Badge>
                    <span className="ms-2">
                      {advertisement.color_diversity > 3 ? 'Многоцветный' : 
                       advertisement.color_diversity > 2 ? 'Двухцветный' : 'Однотонный'}
                    </span>
                  </div>
                </div>
              )}
              
              {advertisement.body_proportions !== null && (
                <div className="metric-item mb-3">
                  <label>Пропорции тела</label>
                  <div className="d-flex align-items-center">
                    <Badge bg="info">
                      {advertisement.body_proportions.toFixed(2)}
                    </Badge>
                    <span className="ms-2">
                      {advertisement.body_proportions > 1.5 ? 'Вытянутое' : 
                       advertisement.body_proportions < 0.8 ? 'Компактное' : 'Нормальное'}
                    </span>
                  </div>
                </div>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  const renderAIAnalysisInfo = () => {
    if (!advertisement.ai_analyzed) return null;

    return (
      <Alert variant="info" className="mb-4">
        <div className="d-flex align-items-center">
          <FaBrain className="me-2" />
          <div>
            <strong>Проанализировано с помощью ИИ</strong>
            {advertisement.ai_confidence && (
              <Badge bg={getConfidenceColor(advertisement.ai_confidence)} className="ms-2">
                Уверенность: {formatConfidence(advertisement.ai_confidence)}
              </Badge>
            )}
            <div className="mt-1">
              <small className="text-muted">
                Характеристики питомца определены автоматически с помощью нейронной сети
              </small>
            </div>
          </div>
        </div>
      </Alert>
    );
  };

  const renderExtendedCharacteristics = () => {
    const hasExtended = advertisement.size || advertisement.coat_type || 
                       advertisement.body_type || advertisement.estimated_age ||
                       advertisement.weight_estimate || advertisement.temperament;

    if (!hasExtended) return null;

    const translations = {
      // Размеры
      'tiny': 'Очень маленький',
      'small': 'Маленький', 
      'medium': 'Средний',
      'large': 'Большой',
      'extra_large': 'Очень большой',
      
      // Типы шерсти
      'short': 'Короткошерстный',
      'medium': 'Среднешерстный',
      'long': 'Длинношерстный',
      'curly': 'Кудрявый',
      'wire': 'Жесткошерстный',
      'hairless': 'Бесшерстный',
      
      // Типы телосложения
      'compact': 'Компактное',
      'normal': 'Нормальное',
      'elongated': 'Вытянутое',
      'muscular': 'Мускулистое',
      'slim': 'Стройное'
    };

    return (
      <Card className="mb-4">
        <Card.Header>
          <h5><FaStar className="me-2" />Дополнительные характеристики</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              {advertisement.size && (
                <div className="characteristic-item mb-2">
                  <strong>Размер:</strong> {translations[advertisement.size] || advertisement.size}
                </div>
              )}
              
              {advertisement.coat_type && (
                <div className="characteristic-item mb-2">
                  <strong>Тип шерсти:</strong> {translations[advertisement.coat_type] || advertisement.coat_type}
                </div>
              )}
              
              {advertisement.body_type && (
                <div className="characteristic-item mb-2">
                  <strong>Телосложение:</strong> {translations[advertisement.body_type] || advertisement.body_type}
                </div>
              )}
            </Col>
            
            <Col md={6}>
              {advertisement.estimated_age && (
                <div className="characteristic-item mb-2">
                  <strong>Примерный возраст:</strong> {advertisement.estimated_age}
                </div>
              )}
              
              {advertisement.weight_estimate && (
                <div className="characteristic-item mb-2">
                  <strong>Примерный вес:</strong> {advertisement.weight_estimate}
                </div>
              )}
              
              {advertisement.temperament && (
                <div className="characteristic-item mb-2">
                  <strong>Характер:</strong> {advertisement.temperament}
                </div>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  return (
    <div className="pet-metrics-display">
      {renderAIAnalysisInfo()}
      {renderAIMetrics()}
      {renderExtendedCharacteristics()}
    </div>
  );
};

export default PetMetricsDisplay; 