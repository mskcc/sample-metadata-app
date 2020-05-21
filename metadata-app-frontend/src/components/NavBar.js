/* eslint-disable react/prop-types */
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import { withRouter } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Button } from '@material-ui/core';
import { logout } from '../actions/UserActions';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  appBar: {
    backgroundColor: '#007CBA',
    height: 50,
  },
  title: {
    flexGrow: 1,
  },
  logoutButton: {
    height: 30,
    fontSize: 12,
    marginBottom: 5,
    justifyContent: 'center',
  },
}));

const NavBar = () => {
  const classes = useStyles();
  //initialize variable from redux state.
  const user = useSelector((state) => state.user);
  const username =
    user && user.data && user.data.username ? user.data.username : null;
  const accessToken =
    user && user.data && user.data.access_token ? user.data.access_token : null;
  const dispatch = useDispatch();

  // function to log out user on button click.
  const handleLogout = (props) => {
    const headers = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const data = {
      username,
    };
    dispatch(logout(data, headers));
    if (!accessToken) {
      props.history.push('/');
    }
  };

  return (
    <div className={classes.root}>
      <AppBar className={classes.appBar} position="static">
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            SSOT
          </Typography>
          {/* Display logout button on NavBar only if user is logged in*/}
          {user && user.data && user.data.access_token && (
            <div>
              <Button
                className={classes.logoutButton}
                variant="outlined"
                color="inherit"
                onClick={handleLogout}
              >
                LOGOUT
              </Button>
            </div>
          )}
        </Toolbar>
      </AppBar>
    </div>
  );
};
export default withRouter(NavBar);
