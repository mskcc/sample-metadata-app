import React, {Component} from 'react';
import NavBar from '../components/NavBar';
import Home from '../components/Home';
// import DevTools from '../components/devtools';

class HomeView extends Component{

    render(){
        return(
            <div>
                <NavBar/>
                <Home/>
                {/* <DevTools/> */}
            </div>
        );
    }
}

export default HomeView;