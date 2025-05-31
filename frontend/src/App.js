import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import 'bootstrap/dist/css/bootstrap.min.css';
import LandingPage from './components/pages/LandingPage'
import LoginPage from './components/pages/LoginPage'
import RegisterPage from './components/pages/RegisterPage'
import HomePage from './components/pages/HomePage'
import ProfilePage from './components/pages/ProfilePage'
import SearchByLocation from './components/pages/SearchByLocation';
import SearchByPost from './components/pages/SearchByPost';
import PetProfile from './components/pages/PetProfile';
import MyAdvertisements from './components/pages/MyAdvertisements';
import AdvertisementDetails from './components/pages/AdvertisementDetails';
import EnhancedPetAnalysis from './components/pages/EnhancedPetAnalysis';
import './App.css'

const App = () => {
    return (
        <Router>
            <div>
                <Switch>
                    <Route exact path="/" component={LandingPage} />
                    <Route path="/login" component={LoginPage} />
                    <Route path="/register" component={RegisterPage} />
                    <Route path="/home" component={HomePage} />
                    <Route path="/profile" component={ProfilePage} />
                    <Route path="/search-by-location" component={SearchByLocation} />
                    <Route path="/search-by-post" component={SearchByPost} />
                    <Route path="/enhanced-analysis" component={EnhancedPetAnalysis} />
                    <Route path="/post/new" component={PetProfile} />
                    <Route path="/post/:id" component={PetProfile} />
                    <Route path="/advertisement/:id" component={AdvertisementDetails} />
                    <Route path="/my-advertisements" component={MyAdvertisements} />
                </Switch>
            </div>
        </Router>
    );
};

export default App;
