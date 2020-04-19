import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import { withRouter } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { Button } from "@material-ui/core";
import { logout } from "../actions/UserActions";

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  title: {
    flexGrow: 1
  }
}));

const NavBar = props => {
  const classes = useStyles();
  const user = useSelector(state => state.user);
  const username =
    user && user.data && user.data.username ? user.data.username : null;
  const access_token =  user && user.data && user.data.access_token ? user.data.access_token : null;
  const dispatch = useDispatch();
  console.log("access token: " + access_token);

  const handleLogout = props => {
    var headers = {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        Authorization: "Bearer " + user.data.access_token
      }
    };
    let data = {
      username: username
    };
    dispatch(logout(data, headers));
    if(!access_token){
      props.history.push("/");
    }
  };

  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            SSOT
          </Typography>
          {user && user.data && user.data.access_token && (
            <div>
              <Button variant="outlined" color="inherit" onClick={handleLogout}>
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
