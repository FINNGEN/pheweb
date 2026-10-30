/* eslint-env jest */

import { createTitle } from "./Coding";
import { parseQuery, queryToPath } from "./CodingSearch";
import { nullLastSort, pValueRepr } from "./CodingColumns";

test('coding title', () => {
    expect(createTitle(undefined)).toBe("coding");
    expect(createTitle("TEST")).toBe("coding TEST");
})

test('parse variant queries', () => {
    expect(parseQuery("1-12345-a-g")).toEqual({ variant: "1-12345-A-G" });
    expect(parseQuery("chr23:100:C:T")).toEqual({ variant: "X-100-C-T" });
    expect(parseQuery(" x_100_C_T ")).toEqual({ variant: "X-100-C-T" });
})

test('parse gene queries', () => {
    expect(parseQuery("brca2")).toEqual({ gene: "BRCA2" });
    expect(parseQuery("rs123")).toEqual({ gene: "RS123" });
    expect(queryToPath("pcsk9")).toBe("/coding/gene/PCSK9");
    expect(queryToPath("1-5-C-T")).toBe("/coding/variant/1-5-C-T");
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
