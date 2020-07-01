import React, { useState } from 'react';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import { withRouter } from 'react-router-dom';
import { HotTable } from '@handsontable/react';
import '../index.css';
import { Button, Typography } from '@material-ui/core';
import { useSelector, useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import { UserViewConfigDialog } from './UserViewConfigDialog';
import { saveChanges } from '../actions/SaveActions';
import { ADMIN_EMAIL } from '../configs/react.configs';

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
  handsontable: {
    paddingBottom: 20,
  },
  filter: {
    margin: theme.spacing(1),
    display: 'flex',
    alignItems: 'center',
  },
  button: {
    margin: theme.spacing(1),
    backgroundColor: '#007CBA',
  },
  useralert: {
    color: 'red',
    textAlign: 'center',
    fontFamily: 'sans-serif',
    fontSize: 15,
    margin: 20,
  },
}));

const DataGrid = (props) => {
  const classes = useStyles();

  //get data for setup from props
  const [gridData, setGridData] = useState(props.gridData); //data to show in grid
  const colDefs = props.colDefs; //column to data mapings definitions for grid columns
  const colHeaders = props.colHeaders; //column settings for grid
  const [settings, setSettings] = useState(props.settings); //other settings for the grid.
  let columnsToHide =
    settings && settings.hiddenColumns && settings.hiddenColumns.columns; //columns that are hidden but can be unhidden.
  const [saveChangesDisabled, setSaveChangesDisabled] = useState(true); // state variable used to set save button enabled or disabled
  const [dataRowsEdited, setDataRowsEdited] = useState(new Set()); // state variable to hold the data rows where one of the column values is edited.
  const [hiddenColumnsChanged, setHiddenColumnsChanged] = useState(false); // state variable to hold hide/show column selections by user.
  const user = useSelector((state) => state.user); //get user data from redux state.
  const userRole =
    user && user.data && user.data.access_token ? user.data.role : null; //get user role.
  const accessToken =
    user && user.data && user.data.access_token ? user.data.access_token : null; //get access token for server requests.

  const dispatchSave = useDispatch(); //initialize variable to dispatch action to save edited data rows.
  console.log(settings);
  // this is the method to set the grid height equivalent to 50% of the browser window size.
  const setGridHeight = () => {
    return window.innerHeight * 0.5;
  };

  //When a row cell is edited add the id of that row object to state in a Set(). We will use this Set object to filter data rows to save to DB to make save operation faster.
  const handleEdit = (changes, source) => {
    if (changes) {
      let editedRowIds = changes.map((change) => {
        return gridData[change[0]].id;
      });
      let newSet = new Set(editedRowIds);
      let updatedEditedRowSet = new Set([...dataRowsEdited, ...newSet]);
      setDataRowsEdited(updatedEditedRowSet);
      setSaveChangesDisabled(false);
    }
  };

  // Method to filter grid data based on value entered in input box above the grid data.
  const filterResults = (e) => {
    let filterText = e.target.value;
    if (filterText) {
      const data = gridData.filter((item) => {
        return Object.values(item)
          .map((value) => {
            return String(value).toLowerCase();
          })
          .find((value) => {
            return value && value.includes(filterText.toLowerCase());
          });
      });
      setGridData(data);
    } else {
      setGridData(props.gridData);
    }
  };

  //Method to save data changes made by user when save button is clicked.
  //First filter the table for only rows that were edited and needs to be saved. Save the filtered rows.
  const saveDataChanges = () => {
    const rowsToSave = gridData.filter((item) => {
      return dataRowsEdited.has(item.id);
    });
    const headers = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        Authorization: `Bearer ${accessToken}`,
      },
    };
    //dispatch action to save datagrid chages to db
    dispatchSave(saveChanges(rowsToSave, headers));
    //disable the save changes button after dispatching saveChanges action.
    setSaveChangesDisabled(true);
    setDataRowsEdited(new Set());
  };

  // Method to update the hiddenColumn values in handsontable settings as user
  // toggle the columns to hide. This method is passed as prob to
  const handleUserConfigChange = (newHiddenColConfigs) => {
    const updatedSettings = settings;
    updatedSettings.hiddenColumns.columns = newHiddenColConfigs;
    setSettings(updatedSettings);
    setHiddenColumnsChanged(!hiddenColumnsChanged);
  };

  return (
    <div className={classes.root}>
      {userRole && userRole === 'user' && 
        <div className={classes.useralert}>
          You are logged in as a regular user. If you are a clinician, please
          email administrators at '{ADMIN_EMAIL}' to get access to
          clinical data.
        </div>
      }
      <Paper className={classes.paper}>
        <div className={classes.filter}>
          {/*Text field above the grid to filter grid data based on text field value. */}
          {gridData.length > 0 && (
            <TextField
              className={classes.filter}
              id="filter-data"
              margin="dense"
              size="small"
              label="filter grid data"
              variant="outlined"
              onChange={(event) => filterResults(event)}
            />
          )}
          {/*For Admin roles, a button to save changes made to data in grid. 
          The button is enabled after edits are made in the grid. And disabled after changes are saved.*/}
          {gridData.length > 0 && userRole && userRole === 'admin' && (
            <Button
              className={classes.button}
              color="primary"
              variant="contained"
              disabled={saveChangesDisabled}
              onClick={() => {
                saveDataChanges();
              }}
            >
              Save Changes
            </Button>
          )}
          {/*Text showing the number of results returned by search */}
          <Typography>Total Results: {gridData.length}</Typography>

          {gridData.length > 0 && (
            <UserViewConfigDialog
              columnNames={colHeaders}
              columnsToHide={columnsToHide}
              handleUserConfigChange={handleUserConfigChange}
            />
          )}
        </div>
        {gridData.length > 0 && (
          <div className={classes.handsontable}>
            <HotTable
              className="handsontable"
              data={gridData}
              colHeaders={colHeaders}
              columns={colDefs}
              settings={settings}
              afterChange={(changes, source) => handleEdit(changes, source)}
              stretchH="all"
              licenseKey="non-commercial-and-evaluation"
              height={setGridHeight}
              wordWrap={false}
              autoRowSize={false}
              search={true}
              currentRowClassName="currentRow"
              currentColClassName="currentCol"
            />
          </div>
        )}
      </Paper>
    </div>
  );
};
DataGrid.propTypes = {
  gridData: PropTypes.array.isRequired,
  colDefs: PropTypes.array.isRequired,
  colHeaders: PropTypes.array.isRequired,
  settings: PropTypes.object.isRequired,
};
export default withRouter(DataGrid);
