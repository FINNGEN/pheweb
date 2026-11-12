/* eslint-env jest */

import { createTitle } from "./Coding";
import { nullLastSort, pValueRepr } from "./CodingColumns";

test('coding title', () => {
    expect(createTitle(undefined)).toBe("coding");
    expect(createTitle("TEST")).toBe("coding TEST");
})

test('nulls sort last in both directions', () => {
    // react-table reverses the result for descending sort
    const sort = (values, desc) => [...values].sort((a, b) => (desc ? -1 : 1) * nullLastSort(a, b, desc));
    expect(sort([2, null, "inf", 1], false)).toEqual([1, 2, "inf", null]);
    expect(sort([2, null, "inf", 1], true)).toEqual(["inf", 2, 1, null]);
})

test('p-value representation', () => {
    expect(pValueRepr(2)).toBe("1.00e-2");
    expect(pValueRepr(400)).toBe("1e-400");
})
