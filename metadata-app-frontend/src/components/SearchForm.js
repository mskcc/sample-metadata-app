import React, { useState, useEffect } from "react";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Paper from "@material-ui/core/Paper";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
import InputLabel from "@material-ui/core/InputLabel";
import { makeStyles } from "@material-ui/core/styles";
import { withRouter } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { searchdata } from "../actions/SearchActions";
import { requestHeaders } from "../configs/react.configs";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: "center",
    color: theme.palette.text.secondary,
  },
  submit: {
    margin: theme.spacing(2),
    backgroundColor: '#007CBA',
  },
  formControl: {
    margin: theme.spacing(2),
    minWidth: 150,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  inputBox:{
    height:30,
    fontSize:12,
    width:300
  },
  checkbox:{
    marginTop:"20px", 
    fontSize:10,
  },
  selectBox:{
    height:28,
  },
  selectMenuItem:{
    fontSize: 12,
  }
}));

const SearchForm = (props) => {
  const classes = useStyles();

  //search text values/hooks
  const [userinput, setUserinput] = useState("");
  const [userinputError, setUserinputError] = useState(false);
  const [userinputEdited, setUserinputEdited] = useState(false);

  //search type select box values/hooks
  const [searchtype, setSearchtype] = useState("");
  const [searchtypeError, setSearchtypeError] = useState(false);
  const [searchtypeEdited, setSearchtypeEdited] = useState(false);
  const [application, setApplication] = useState(false);
  const [applicationEdited, setApplicationEdited] = useState(false);

  //checkbox fields
  const [exactMatch, setExactMatch] = useState(false);
  const [hasData, setHasData] = useState(false);

  //get user info/values from store
  const user = useSelector((state) => state.user);
  const access_token =
    user && user.data && user.data.access_token ? user.data.access_token : null;
  const role = user && user.data && user.data.role ? user.data.role : null;
  const recipes = user && user.data && user.data.recipes ? user.data.recipes : null;
  const dispatchSearch = useDispatch();

  //validate if the user is logged in. Redirect to login page if user is not logged in.
  useEffect(() => {
    if (!access_token) {
      props.history.push("/");
    }
  });

  //handle search text change
  const handleInputChange = (text) => {
    setUserinput(text);
    if (text.length > 0) {
      setUserinputError(false);
      setUserinputEdited(true);
    }else if(userinputEdited && text.length===0) {
      setUserinputError(true);
    }
  };

  //handle search type change
  const handleSearchtypeChange = (text) => {
    setSearchtype(text);
    if (text && text.length > 0) {
      setSearchtypeError(false);
      setSearchtypeEdited(true);
    } else {
      setSearchtypeError(false);
    }
  };

  const handleApplicationChange =(text)=>{
    setApplication(text);
    if (text && text.length > 0) {
      setApplicationEdited(true);
    } else {
      setSearchtypeError(false);
    }
  }
  //handle form submit
  const handleSubmit = (event) => {
    event.preventDefault();
    searchtype === "" ? setSearchtypeError(true) : setSearchtypeError(false);

    userinput.length === 0 && !userinputEdited
      ? setUserinputError(true)
      : setUserinputError(false);

    if (userinput && !userinputError && searchtype && !searchtypeError) {
      let state = {
        userinput: userinput,
        searchtype: searchtype,
        user_role: role,
      };
      let headers = requestHeaders;
      headers.Authorization = "Bearer " + access_token;
      dispatchSearch(searchdata(state, headers));
    }
  };

  return (
    <div className={classes.root}>
      <Grid container justify="center" spacing={3}>
        <Grid item xs={12}>
          <Paper className={classes.paper}>
            <Grid container justify="center" spacing={3}>
              <Grid item xs={9} sm={6} >
                <TextField
                  className={classes.inputBox}
                  margin="dense"
                  variant="standard"
                  label="search keyword(s)"
                  fullWidth
                  required
                  // multiline
                  // rowsMax="2"
                  value={userinput}
                  error={userinputError}
                  helperText={userinputError && "Search keyword is required."}
                  onChange={(event) => handleInputChange(event.target.value)}
                />
              </Grid>
              <Grid item xs={6}  sm={3}>
                <FormControl
                  className={classes.formControl}
                  error={searchtypeError}
                >
                  <InputLabel>
                    search type
                  </InputLabel>
                  <Select
                    className={classes.selectBox}
                    margin="dense"
                    value={searchtype}
                    onChange={(event) =>
                      handleSearchtypeChange(event.target.value)
                    }
                  >
                    <MenuItem className={classes.selectMenuItem} value="mrn">mrn</MenuItem>
                    <MenuItem className={classes.selectMenuItem} value="tumor type">tumor type</MenuItem>
                    <MenuItem className={classes.selectMenuItem} value="patient id">patient id</MenuItem>
                    <MenuItem className={classes.selectMenuItem} value="all records">all records</MenuItem>
                  </Select>
                  {searchtypeError && (
                    <FormHelperText>search type required</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              {searchtype && searchtype === "tumor type" &&
              <Grid item xs={6} sm={3}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={exactMatch}
                      onChange={()=> setExactMatch(!exactMatch)}
                      name="exactMatch"
                      
                    />
                  }
                  label="Exact Match"
                  className={classes.checkbox}
                />
              </Grid>
              }
            </Grid>
            <Grid container justify="center" spacing={3}>
            <Grid item xs={9}  sm={6}>
                <FormControl
                  className={classes.formControl}
                  error={searchtypeError}
                >
                  <InputLabel>
                    Application type
                  </InputLabel>
                  <Select
                    className={classes.selectBox}
                    margin="dense"
                    value={application}
                    onChange={(event) =>
                      handleApplicationChange(event.target.value)
                    }
                  >
                    <MenuItem className={classes.selectMenuItem} value="All">All</MenuItem>
                    {recipes && recipes.map((recipe, index)=>
                      <MenuItem className={classes.selectMenuItem} key={index} value={recipe}>{recipe}</MenuItem>
                    )}
                  </Select>
                  {searchtypeError && (
                    <FormHelperText>search type required</FormHelperText>
                  )}
                </FormControl>
              </Grid>
      

              <Grid item xs={6}  sm={3}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={hasData}
                      onChange={() => setHasData(!hasData)}
                      name="checkedG"
                    />
                  }
                  label="Has Data"
                  className={classes.checkbox}
                />
              </Grid>
            </Grid>
            <Grid container justify="center" spacing={3}>
              <Grid item xs={6} sm={3}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  className={classes.submit}
                  onClick={(event) => handleSubmit(event)}
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

export default withRouter(SearchForm);
