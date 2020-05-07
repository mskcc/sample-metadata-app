import React, { useState, useEffect} from "react";
import Avatar from "@material-ui/core/Avatar";
import Button from "@material-ui/core/Button";
import CssBaseline from "@material-ui/core/CssBaseline";
import TextField from "@material-ui/core/TextField";
import Link from "@material-ui/core/Link";
import Box from "@material-ui/core/Box";
import LockOutlinedIcon from "@material-ui/icons/LockOutlined";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import Container from "@material-ui/core/Container";
import { withRouter } from "react-router-dom";
import {BackDrop} from './BackDrop';
import {login} from '../actions/UserActions';
import { useSelector, useDispatch } from "react-redux";
import { SnackBar } from "./SnackBar";

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {"Copyright © "}
      <Link color="inherit" href="#">
        CMO
      </Link>{" "}
      {new Date().getFullYear()}
      {"."}
    </Typography>
  );
}

const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(1),
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main
  },
  loginText: {
    color: "blue"
  },
  form: {
    width: "100%", // Fix IE 11 issue.
    marginTop: theme.spacing(1),
    color: "blue"
  },
  submit: {
    margin: theme.spacing(3, 0, 2)
  },
  backdrop: {
    zIndex: theme.zIndex.drawer + 1,
    color: '#fff',
  },
}));

const Login = (props) => {
  const classes = useStyles();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [usernameError, setUsernameError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const [usernameEdited, setUsernameEdited]=useState(false);
  const [passwordEdited, setPasswordEdited]=useState(false);

  const isFetching = useSelector(state => state.isFetching);
  const user = useSelector(state => state.user);
  const access_token = user && user.data && user.data.access_token ? user.data.access_token : null;
  const dispatchLogin = useDispatch();


  useEffect(()=>{
    if(access_token){
      props.history.push("/home");
    }
  });

  const handleUsernameChange = (text) => {
    setUsername(text);
    if(text.length > 0 ){
      setUsernameError(false);
      setUsernameEdited(true);
    }else{
      setUsernameError(true);
    }
  }
  
  const handlePasswordChange = (text) => {
    setPassword(text);
    if(text.length > 0 ){
      setPasswordError(false);
      setPasswordEdited(true);
    }else{
      setPasswordError(true);
    }
  }

  const handleSubmit = event => {
    event.preventDefault();
    (username.length === 0 && !usernameEdited) ? setUsernameError(true): setUsernameError(false);
    (password.length === 0 && !passwordEdited) ? setPasswordError(true) : setPasswordError(false);
    if (usernameEdited && !usernameError && passwordEdited && !passwordError) {
      let data = {
        username: username,
        password: password,
      }
      dispatchLogin(login(data));
    }
  };


  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography className={classes.loginText} component="h1" variant="h5">
          Sign in
        </Typography>
        {isFetching && <BackDrop className={classes.backdrop} isFetching = {isFetching}/>}
        {user && user.data && user.data.access_token ? <SnackBar open severity="success" message={user.data.message}/> : null }
        <form className={classes.form} method="POST">
          <TextField
            variant="standard"
            margin="normal"
            required
            fullWidth
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            error={usernameError}
            helperText={usernameError && "username is required"}
            value={username}
            onChange={event => handleUsernameChange(event.target.value)}
          />
          <TextField
            variant="standard"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            error={passwordError}
            helperText={passwordError && "password is required"}
            value={password}
            onChange={event => handlePasswordChange(event.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
            onClick={event => handleSubmit(event)}
          >
            Sign In
          </Button>
        </form>
      </div>
      <Box mt={8}>
        <Copyright />
      </Box>
    </Container>
  );
};

export default withRouter(Login);