import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import { useSelector, useDispatch } from 'react-redux';
import Checkbox from '@material-ui/core/Checkbox';
import Spinner from './Spinner';
import { saveViewConfigData } from '../actions/SaveActions';
import PropTypes from 'prop-types';

const useStyles = makeStyles((theme) => ({
  form: {
    display: 'flex',
    flexDirection: 'column',
    margin: 'auto',
    width: 'fit-content',
  },
  formControlLabel: {
    marginTop: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(1),
    backgroundColor: '#007CBA',
  },
}));

export const UserViewConfigDialog = (props) => {
  const classes = useStyles();

  //get values from props
  const { columnNames, columnsToHide } = props;
  const [open, setOpen] = useState(false);
  const [hiddenColumns, setHiddenColumns] = useState(null);
  const [checked, setChecked] = useState(false);

  //initialize redux dispatch variable
  const dispatchSaveViewConfigs = useDispatch();
  //get values from redux state
  const viewConfigs = useSelector((state) => state.savedUserConfigResults);
  const user = useSelector((state) => state.user);
  const accessToken =
    user && user.data && user.data.access_token ? user.data.access_token : null;

  //initialize columns to hide using values from props.
  useEffect(() => {
    if (columnsToHide && !hiddenColumns) {
      let hideColumnConfigs = columnNames.map((item, index) => {
        let obj = {};
        obj.index = index;
        obj.label = item;
        obj.isChecked = columnsToHide.includes(index);
        return obj;
      });
      setHiddenColumns(hideColumnConfigs);
    }
  }, []);

  //to toggle dialog component
  const handleDialogState = () => {
    setOpen(true);
  };

  //to toggle dialog component on close button click.
  const handleClose = () => {
    setOpen(false);
  };

  //to save configs upon save button click.
  const handleSave = () => {
    let newHiddenColumns = [];
    hiddenColumns.forEach((item) => {
      if (item.isChecked) {
        newHiddenColumns.push(item.index);
      }
    });
    const headers = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const data = {
      hiddenColumns: newHiddenColumns,
    };
    //dispatch save action
    dispatchSaveViewConfigs(saveViewConfigData(data, headers));
    setChecked(!checked); // this is a dummy method to force state update immediately
    if (viewConfigs && !viewConfigs.isFetching) {
      setOpen(false); //close dialog after save action is complete.
    }
  };

  //add columns marked as hidden by user to hiddenColumns variable to update the grid view.
  const handleChange = (index, event) => {
    hiddenColumns.forEach((item) => {
      if (item.index === index) item.isChecked = event.target.checked;
    });
    setChecked(!checked);
    //fire function to update state in the parent component (DataGrid) to update Grid view state.
    handleViewConfigsChange();
  };

  const handleViewConfigsChange = () => {
    //get the updated hiddenColumns as user toggles column state in the pop up dialog.
    let newHiddenColumns = [];
    hiddenColumns.forEach((item) => {
      if (item.isChecked) {
        newHiddenColumns.push(item.index);
      }
    });
    //fire the parent component function passed as prop to update state of parent component(DataGrid) to update Grid view state.
    props.handleUserConfigChange(newHiddenColumns);
  };

  return (
    <div>
      <Button
        className={classes.button}
        color="primary"
        variant="contained"
        onClick={handleDialogState}
      >
        HIDE COLUMNS
      </Button>
      <Dialog
        fullWidth={false}
        maxWidth="xs"
        open={open}
        onClose={handleClose}
        onBackdropClick={handleClose}
        aria-labelledby="show-hide-columns"
      >
        <DialogTitle id="show-hide-columns-title">
          Check To Hide Columns
        </DialogTitle>
        <DialogContent>
          {viewConfigs && viewConfigs.isFetching && <Spinner />}
          <form className={classes.form} noValidate>
            {hiddenColumns &&
              hiddenColumns.map((item, index) => (
                <FormControlLabel
                  className={classes.formControlLabel}
                  control={
                    <Checkbox
                      key={index}
                      checked={item.isChecked}
                      onChange={(event) => handleChange(item.index, event)}
                    />
                  }
                  label={item.label}
                  key={index}
                />
              ))}
          </form>
        </DialogContent>
        <DialogActions>
          <Button
            className={classes.button}
            color="primary"
            variant="contained"
            onClick={handleSave}
          >
            Save
          </Button>
          <Button
            className={classes.button}
            color="primary"
            variant="contained"
            onClick={handleClose}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
//validate component props.
UserViewConfigDialog.propTypes = {
  columnNames: PropTypes.array.isRequired,
  columnsToHide: PropTypes.array.isRequired,
  handleUserConfigChange: PropTypes.func.isRequired,
};
