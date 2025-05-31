import React, { Component } from 'react';
import { Marker, InfoWindow } from 'google-maps-react';

class PetMarker extends Component {
  state = {
    showInfoWindow: false,
  };

  onMarkerClick = () => {
    this.setState({ showInfoWindow: true });
  };

  onInfoWindowClose = () => {
    this.setState({ showInfoWindow: false });
  };

  render() {
    const { pet } = this.props;
    const { showInfoWindow } = this.state;

    return (
      <Marker onClick={this.onMarkerClick} name={pet.name} position={{ lat: pet.lat, lng: pet.lng }}>
        {showInfoWindow && (
          <InfoWindow onClose={this.onInfoWindowClose}>
            <div>
              <h4>{pet.name}</h4>
              <p>{pet.description}</p>
            </div>
          </InfoWindow>
        )}
      </Marker>
    );
  }
}

export default PetMarker;