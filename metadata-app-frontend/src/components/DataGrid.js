import React from "react";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import { withRouter } from "react-router-dom";
import { HotTable } from "@handsontable/react";
import "../index.css";

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    margin: theme.spacing(2),
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: "center",
    color: theme.palette.text.secondary,
  },
  searchresults: {
    marginLeft: "20px",
    color: "black",
  },
  handsontable: {
    paddingBottom: 20,
  },
}));

const DataGrid = (props) => {
  const classes = useStyles();

  //get user info/values from store
  const gridData = props.gridData;
  const colDefs = props.colDefs;
  const colHeaders = props.colHeaders;
  const settings = props.settings;
  const dataSize = gridData ? gridData.length : 0;

  const setGridHeight = () => {
    return window.innerHeight * 0.65;
  };

  //When a row cell is edited add the id of that row object to state in a Set(). We will use this Set object to filter data rows to save to DB to make save operation faster.
  const handleEdit = (changes, source) => {
    changes &&
      changes.map((change) => {
        this.setState({
          dataRowsEdited: new Set([
            ...this.state.dataRowsEdited,
            this.state.tableData[change[0]].id,
          ]),
        });
        this.setState({ isSaveButtonDisabled: false });
      });
  };

  return (
    <div className={classes.root}>
      <Paper className={classes.paper}>
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
      </Paper>
    </div>
  );
};

export default withRouter(DataGrid);
