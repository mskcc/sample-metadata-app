import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import LoginView from './views/LoginView';
import HomeView from './views/HomeView';
import { BASE_ROUTE} from './configs/react.configs';

class App extends Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <Router basename={BASE_ROUTE}>
          <Switch>
            <Route path="/" exact component={LoginView} />
            <Route path="/home" exact component={HomeView} />
          </Switch>
        </Router>
      </MuiThemeProvider>
    );
  }
}


const theme = createMuiTheme({
  typography: {
    useNextVariants: true,
  },
  palette: {
    primary: {
      logo: '#319ae8',
      light: '#8FC7E8',
      main: '#007CBA',
      dark: '#006098',
    },
    secondary: {
      light: '#F6C65B',
      main: '#DF4602',
      dark: '#C24D00',
    },

    textSecondary: '#e0e0e0',
  },
});


export default App;
