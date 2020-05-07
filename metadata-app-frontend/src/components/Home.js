import React, { useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { withRouter } from "react-router-dom";
import { useSelector } from "react-redux";
import SearchForm from "./SearchForm";
import { Spinner } from "./Spinner";
import DataGrid from './DataGrid';
import '../index.css';

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
  //get user info/values from store
  // const isFetching = useSelector(state => state.isFetching);
  const user = useSelector(state => state.user);
  const access_token =
    user && user.data && user.data.access_token ? user.data.access_token : null;

  const searchresults = useSelector(state=> state.searchresults);
  const fetchingSearchResults = searchresults && searchresults.isFetching;
  const gridData = searchresults.data ? JSON.parse(searchresults.data.data) : null;
  const colHeaders = searchresults.data ? searchresults.data.col_headers : null;
  const colDefs = searchresults.data ? searchresults.data.column_defs : null;
  const settings = searchresults.data ? searchresults.data.settings: null;

  //validate if the user is logged in. Redirect to login page if user is not logged in.
  useEffect(() => {
    if (!access_token) {
      props.history.push("/");
    }
  });


  return (
    <div className={classes.root}>
      <SearchForm/>
      {fetchingSearchResults ? <Spinner/> :
      gridData && <DataGrid gridData = {gridData} colHeaders = {colHeaders} colDefs={colDefs} settings={settings} />}
     </div>
  );
};

export default withRouter(Home);
