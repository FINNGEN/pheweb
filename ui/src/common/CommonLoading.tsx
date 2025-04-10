import React, { useState } from "react";

const commonLoading: JSX.Element = <div>... loading ...</div>

export const isLoading = (isLoading: boolean, content: () => JSX.Element): JSX.Element => {
  if (isLoading) {
    return commonLoading;
  } else {
    return content();
  }
}

export const CommonLoadingMoreOrLess = (qc_variant_results: any) => {
  const [showMore, setShowMore] = useState(false);

  const toggleColumns = () => {
    setShowMore(prev => !prev);
  };
  return <>
    <div style={{ color: '#007bff', textDecoration: 'none', cursor: 'pointer' }} onClick={toggleColumns}>
      {showMore ? 'Show Less' : 'Show More'}
    </div>
    <div style={showMore ? { display: 'block' } : { display: 'none' }}>
      {showMore ? (
        <pre style={{ backgroundColor: '#f6f8fa', padding: '1rem', borderRadius: '5px' }}>
          <code>{JSON.stringify(qc_variant_results, null, 2)}</code>
        </pre>
      ) : ''}
    </div>
  </>
}

export const commonErrorTable = (qcVariantMessage: string | null | undefined, content: JSX.Element, qcVariant: any): JSX.Element => {
  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse' as 'collapse',  // Correctly specifying the value type
    margin: '16px 0'
  };

  return <div>
    {(qcVariantMessage === null || qcVariantMessage === undefined) ? (
      content
    ) : (
      <div>
        <b>Sorry!</b>: {qcVariantMessage}
        <table style={tableStyle}>
          <thead>
            <tr>
              <th>Variant</th>
              <th>Failed filter</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{qcVariant['variant']}</td>
              <td>{qcVariant['failed_filter']}</td>
            </tr>
          </tbody>
        </table>
        <CommonLoadingMoreOrLess qc_variant_results={qcVariant} />
      </div>
    )}
  </div>
}

export const hasError = (errorMessage: string | null | undefined, content: JSX.Element): JSX.Element => {
  if (errorMessage === null || errorMessage === undefined) {
    return content
  } else {
    return <div><b>Error</b> : {errorMessage}</div>
  }
}
export default commonLoading
