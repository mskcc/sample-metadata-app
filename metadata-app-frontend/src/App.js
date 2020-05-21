import React, { Component } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import LoginView from "./views/LoginView";
import HomeView from "./views/HomeView";
import { BASE_ROUTE } from "./configs/react.configs";

class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <Route path={`${BASE_ROUTE}/`} exact component={LoginView} />
          <Route path={`${BASE_ROUTE}/home`} exact component={HomeView} />
        </Switch>
      </Router>
    );
  }
}

export default App;