import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import { useSelector } from 'react-redux';
import SearchForm from './SearchForm';
import Spinner from './Spinner';
import DataGrid from './DataGrid';
import '../index.css';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    margin: theme.spacing(2),
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  submit: {
    margin: theme.spacing(2),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 150,
  },
  selectEmpty: {
    marginTop: theme.spacing(1),
  },
}));

const Home = (props) => {
  const classes = useStyles();
  //initialize variable from redux state
  const user = useSelector((state) => state.user);
  const access_token =
    user && user.data && user.data.access_token ? user.data.access_token : null;
  const searchResults = useSelector((state) => state.searchResults);
  const fetchingSearchResults = searchResults && searchResults.isFetching;
  const saveDataResults = useSelector((state) => state.saveDataResults);
  const savingResults = saveDataResults && saveDataResults.isFetching;
  //initialize grid data from redux state
  const gridData = searchResults.data
    ? JSON.parse(searchResults.data.data)
    : null;
  const colHeaders = searchResults.data ? searchResults.data.col_headers : null;
  const colDefs = searchResults.data ? searchResults.data.column_defs : null;
  const settings = searchResults.data ? searchResults.data.settings : null;
  //validate if the user is logged in. Redirect to login page if user is not logged in.
  useEffect(() => {
    if (!access_token) {
      props.history.push("/");
    }
  });

  return (
    <div className={classes.root}>
      <SearchForm />
      {savingResults ? <Spinner /> : null}
      {fetchingSearchResults ? (
        <Spinner />
      ) : (gridData && 
          <DataGrid
            gridData={gridData}
            colHeaders={colHeaders}
            colDefs={colDefs}
            settings={settings}
          />
      )}
    </div>
  );
};

export default withRouter(Home);
