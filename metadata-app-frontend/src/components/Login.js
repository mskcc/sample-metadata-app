import React, { useState, useEffect } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import Link from '@material-ui/core/Link';
import Box from '@material-ui/core/Box';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import { withRouter } from 'react-router-dom';
import { login } from '../actions/UserActions';
import { useSelector, useDispatch } from 'react-redux';
import Spinner from './Spinner';

//function to show copyright text at bottom of page.
function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="#">
        CMO
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

//styles declaration.
const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(1),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
    color: ' #007CBA',
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  backdrop: {
    zIndex: theme.zIndex.drawer + 1,
    color: '#fff',
  },
}));

const Login = (props) => {
  const classes = useStyles();
  //state variables
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameError, setUsernameError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);
  const [usernameEdited, setUsernameEdited] = useState(false);
  const [passwordEdited, setPasswordEdited] = useState(false);

  //initialize variable from redux state
  const user = useSelector((state) => state.user);
  const accessToken = user && user.data ? user.data.access_token : null;
  const isFetching = user ? user.isFetching : false;
  //dispatch action constant declaration
  const dispatchLogin = useDispatch();

  //use effect to validate user token. If token is present, redirect user to homepage.
  useEffect(() => {
    if (accessToken) {
      props.history.push("/home");
    }
  });

  //handle changes when user edits text in username TextInput box.
  const handleUsernameChange = (text) => {
    setUsername(text);
    if (text.length > 0) {
      setUsernameError(false);
      setUsernameEdited(true);
    } else {
      setUsernameError(true);
    }
  };

  //handle changes when user edits text in password TextInput box.
  const handlePasswordChange = (text) => {
    setPassword(text);
    if (text.length > 0) {
      setPasswordError(false);
      setPasswordEdited(true);
    } else {
      setPasswordError(true);
    }
  };

  //function is fired when user hits login button.
  const handleSubmit = (event) => {
    event.preventDefault();
    username.length === 0 && !usernameEdited
      ? setUsernameError(true)
      : setUsernameError(false);
    password.length === 0 && !passwordEdited
      ? setPasswordError(true)
      : setPasswordError(false);
    if (usernameEdited && !usernameError && passwordEdited && !passwordError) {
      let data = {
        username: username,
        password: password,
      };
      //fire login action
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
            helperText={usernameError && 'valid username is required'}
            value={username}
            onChange={(event) => handleUsernameChange(event.target.value)}
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
            helperText={passwordError && 'valid password is required'}
            value={password}
            onChange={(event) => handlePasswordChange(event.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
            onClick={(event) => handleSubmit(event)}
          >
            Sign In
          </Button>
        </form>
      </div>
      <div>{isFetching && <Spinner />}</div>
      <Box mt={8}>
        <Copyright />
      </Box>
    </Container>
  );
};

export default withRouter(Login);
