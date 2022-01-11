import React from 'react'
import { Provider } from 'react-redux'

import store from './store'
import { Table } from './ChipTable'

const Chip = (props) => {
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
