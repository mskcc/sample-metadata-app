import React, { useState, useEffect } from "react";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Paper from "@material-ui/core/Paper";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from '@material-ui/core/FormHelperText';
import InputLabel from "@material-ui/core/InputLabel";
import { makeStyles } from "@material-ui/core/styles";
import { withRouter } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { SnackBar } from "./SnackBar";

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,
    margin: theme.spacing(2)
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: "center",
    color: theme.palette.text.secondary
  },
  submit: {
    margin: theme.spacing(2)
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 150
  },
  selectEmpty: {
    marginTop: theme.spacing(1)
  }
}));

const Home = props => {
  const classes = useStyles();

  //search text values/hooks
  const [userinput, setUserinput] = useState("");
  const [userinputError, setUserinputError] = useState(false);
  const [userinputEdited, setUserinputEdited] = useState(false);

  //search type select box values/hooks
  const [searchtype, setSearchtype] = useState(null);
  const [searchtypeError, setSearchtypeError] = useState("");
  const [searchtypeEdited, setSearchtypeEdited] = useState("false");

  //get user info/values from store
  const isFetching = useSelector(state => state.isFetching);
  const user = useSelector(state => state.user);
  const access_token =
    user && user.data && user.data.access_token ? user.data.access_token : null;

  const dispatchLogin = useDispatch();

  //validate if the user is logged in. Redirect to login page if user is not logged in.
  useEffect(() => {
    if (!access_token) {
      props.history.push("/");
    }
  });

  //handle search text change
  const handleInputChange = text => {
    setUserinput(text);
    if (text.length > 0) {
      setUserinputError(false);
      setUserinputEdited(true);
    } else {
      setUserinputError(false);
    }
  };

  //handle search type change
  const handleSearchtypeChange = text => {
    setSearchtype(text);
    if (text && text.length > 0) {
      setSearchtypeError(false);
      setSearchtypeEdited(true);
    } else {
      setSearchtypeError(false);
    }
  };

  //handle form submit
  const handleSubmit = event => {
    event.preventDefault();
    searchtype === null ? setSearchtypeError(true)
    : setSearchtypeError(false);
    
    userinput.length === 0 && !userinputEdited
      ? setUserinputError(true)
      : setUserinputError(false);
    // console.log("userinput edited: " + userinputEdited);
    // console.log("searchtype edited: " + searchtypeEdited);
    // console.log("userinput: " + userinput);
    // console.log("searchtype: " + searchtype);
    // console.log("userinput error: " + userinputError);
    // console.log("searchtype error: " + searchtypeError);

    if (userinput && !userinputError && searchtype && !searchtypeError) {
      let state = {
        userinput: userinput,
        searchtype: searchtype
      };
      console.log(state);
    }
  };

  return (
    <div className={classes.root}>
      <Grid container justify="center" spacing={3}>
        <Grid item xs>
          <Paper className={classes.paper}>
            <Grid container justify="center" spacing={3}>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  variant="standard"
                  label="enter search keyword(s)"
                  fullWidth
                  required
                  multiline
                  rowsMax="4"
                  value={userinput}
                  error={userinputError}
                  helperText={userinputError && "Search keyword is required."}
                  onChange={event => handleInputChange(event.target.value)}
                />
              </Grid>
              <Grid item xs={2}>
                <FormControl className={classes.formControl} error={searchtypeError}>
                  <InputLabel id="demo-controlled-open-select-label">
                    search type
                  </InputLabel>
                  <Select
                    margin="dense"
                    value={searchtype}
                    onChange={event => handleSearchtypeChange(event.target.value)}
                  >
                    <MenuItem value="mrn">mrn</MenuItem>
                    <MenuItem value="tumor type">tumor type</MenuItem>
                    <MenuItem value="patient id">patient id</MenuItem>
                    <MenuItem value="all records">all records</MenuItem>
                  </Select>
                  {searchtypeError && <FormHelperText>search type required</FormHelperText>}
                </FormControl>
              </Grid>
              <Grid item xs={2}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  className={classes.submit}
                  onClick={event => handleSubmit(event)}
                >
                  Search
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};

export default withRouter(Home);
