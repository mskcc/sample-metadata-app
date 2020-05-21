/* eslint-disable react/prop-types */
/* eslint-disable no-unused-vars */
/* eslint-disable no-unused-expressions */
import React, { useState, useEffect } from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import { makeStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import { searchdata } from '../actions/SearchActions';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
    },
  },
  searchinput: {
    width: '75%',
    marginRight: '100',
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  submit: {
    margin: theme.spacing(2),
    backgroundColor: '#007CBA',
    width: '30%',
  },
  checkbox: {
    marginTop: '20px',
    fontSize: 10,
  },
}));

const SearchForm = (props) => {
  const classes = useStyles();

  // search text values/hooks
  const [userinput, setUserinput] = useState('');
  const [userinputError, setUserinputError] = useState(false);
  const [userinputEdited, setUserinputEdited] = useState(false);

  // search type select box values/hooks
  const [searchtype, setSearchtype] = useState('');
  const [searchtypeError, setSearchtypeError] = useState(false);
  const [searchTypeEdited, setSearchtypeEdited] = useState(false);
  const [application, setApplication] = useState(false);
  const [applicationEdited, setApplicationEdited] = useState(false);
  // checkbox fields
  const [exactMatch, setExactMatch] = useState(false);
  const [hasData, setHasData] = useState(false);
  // const [isPublished, setIsPublished] = useState(false);

  // get user info/values from store
  const user = useSelector((state) => state.user);
  const accessToken =
    user && user.data && user.data.access_token ? user.data.access_token : null;
  const role = user && user.data && user.data.role ? user.data.role : null;
  const recipes =
    user && user.data && user.data.recipes ? user.data.recipes : null;
  const dispatchSearch = useDispatch();

  // validate if the user is logged in. Redirect to login page if user is not logged in.
  useEffect(() => {
    if (!accessToken) {
      props.history.push('/');
    }
  });

  // handle search text change
  const handleInputChange = (text) => {
    setUserinput(text);
    if (text.length > 0) {
      setUserinputError(false);
      setUserinputEdited(true);
    } else if (userinputEdited && text.length === 0) {
      setUserinputError(true);
    }
  };

  // handle search type change
  const handleSearchtypeChange = (text) => {
    setSearchtype(text);
    if (text && text.length > 0) {
      setSearchtypeError(false);
      setSearchtypeEdited(true);
    } else {
      setSearchtypeError(false);
    }
  };

  // handle application select box changes
  const handleApplicationChange = (text) => {
    setApplication(text);
    if (text && text.length > 0) {
      setApplicationEdited(true);
    } else {
      setSearchtypeError(false);
    }
  };

  // handle form submit
  const handleSubmit = (event) => {
    event.preventDefault();
    searchtype === '' ? setSearchtypeError(true) : setSearchtypeError(false);

    userinput.length === 0 && !userinputEdited
      ? setUserinputError(true)
      : setUserinputError(false);

    if (userinput && !userinputError && searchtype && !searchtypeError) {
      const state = {
        search_keywords: userinput,
        search_type: searchtype,
        exact_match: exactMatch,
        application,
        has_data: hasData,
        // is_published: isPublished, this will be used when we have source to validate published state of Sample.
        user_role: role,
      };
      const headers = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          Authorization: `Bearer ${accessToken}`,
        },
      };
      // dispatch search action
      dispatchSearch(searchdata(state, headers));
    }
  };

  // values that will show in Search Type select box
  const searchTypeValues = [
    'mrn',
    'patient id',
    'tumor type',
    'igo id',
    'cmo id',
  ];

  return (
    <div>
      <Paper className={classes.paper}>
        <div className={classes.root}>
          <div>
            <TextField
              className={classes.searchinput}
              fullWidth
              margin="dense"
              variant="standard"
              label="enter search keyword(s)"
              required
              size="small"
              value={userinput}
              error={userinputError}
              helperText="Enter (comma, space) separated search values mrn/patient id/tumor type/igo id/cmo id'"
              onChange={(event) => handleInputChange(event.target.value)}
            />
          </div>

          {/* Select field for selection of tumor type */}
          <div>
            <TextField
              id="select-tumor-type"
              required
              select
              error={searchtypeError}
              label="search type"
              value={searchtype}
              style={{ width: '20%' }}
              onChange={(event) => handleSearchtypeChange(event.target.value)}
              helperText="Please select search type"
            >
              {searchTypeValues.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>

            {/* Check box to indicate exact tumor type match when searctype is tumor type. If searchtype is other than tumor type, this checkbox is hidden. */}
            {searchtype && searchtype === 'tumor type' ? (
              <FormControlLabel
                className={classes.checkbox}
                control={
                  <Checkbox
                    size="small"
                    margin="dense"
                    checked={exactMatch}
                    onChange={() => setExactMatch(!exactMatch)}
                    name="exactMatch"
                  />
                }
                label="exact tumortype match"
              />
            ) : (
              ''
            )}

            {/* Select box to allow selection of application for search action */}
            <TextField
              id="select-application"
              select
              label="application type"
              value={application}
              onChange={(event) => handleApplicationChange(event.target.value)}
              helperText="Please select search type"
              style={{ width: '20%' }}
              InputProps={{
                minwidth: '15ch',
              }}
            >
              <MenuItem key={'none'} value={'None'}>
                {'None'}
              </MenuItem>
              {recipes &&
                recipes.map((recipe) => (
                  <MenuItem key={recipe} value={recipe}>
                    {recipe}
                  </MenuItem>
                ))}
            </TextField>

            {/* Checkbox to filter rows that has fastq data values */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={hasData}
                  size="small"
                  margin="dense"
                  onChange={() => setHasData(!hasData)}
                  name="hasDataCheckBox"
                />
              }
              label="has fastq data"
              className={classes.checkbox}
            />

            {/* Checkbox to filter rows where data is published. It is commented out because we currently do not 
            have this value available in db to search. But this logic can be used when we can validate the published 
            state of a Sample. */}
            {/* <FormControlLabel
              control={
                <Checkbox
                  checked={isPublished}
                  size="small"
                  margin="dense"
                  onChange={() => setIsPublished(!isPublished)}
                  name="isPublishedCheckbox"
                />
              }
              label="is published"
              className={classes.checkbox}
            /> */}
          </div>

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
        </div>
      </Paper>
    </div>
  );
};

export default withRouter(SearchForm);
