import React from "react";
import { Provider } from "react-redux";

import store from "./chipStore";
import { Table } from "./ChipTable";
import {setPageTitle} from "../../common/commonUtilities";

interface Props {}

const Chip = () => {
    const title : string = 'chip';
    setPageTitle(title);

    return (
    <Provider store={store}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div
          style={{
            flex: 1,
            height: '100%',
            padding: '10px',
            display: 'flex',
            flexFlow: 'row nowrap',
            justifyContent: 'flex-start',
            flexDirection: 'column'
          }}
        >
          <Table />
        </div>
      </div>
    </Provider>
  )
};

export default Chip;
