import React, { Component } from "react";
import Login from "../components/Login";
import NavBar from "../components/NavBar";
import { withRouter } from "react-router-dom";

//login view component
class LoginView extends Component {
  render() {
    return (
      <div>
        <NavBar />
        <Login />
      </div>
    );
  }
}

export default withRouter(LoginView);
