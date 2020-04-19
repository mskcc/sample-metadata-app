import React, { Component } from "react";
import Login from "../components/Login";
import NavBar from "../components/NavBar";
import { withRouter } from "react-router-dom";
// import DevTools from '../components/devtools';

class LoginView extends Component {
  render() {
    return (
      <div>
        <NavBar />
        <Login />
        {/* <DevTools/> */}
      </div>
    );
  }
}

export default withRouter(LoginView);
