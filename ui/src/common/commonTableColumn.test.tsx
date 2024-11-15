/* eslint-env jest */
import {
  pValueCellFormatter,
  pValueSentinel,
  addHeader,
  nearestGeneFormatter,
  createCSVLinkHeaders,
  filterDownload, optionalCellScientificFormatter,
  optionalCellNumberFormatter, optionalCellDecimalFormatter,
  risteysLinkFormatter,
  risteysURLFormatter,
  risteysLinkCell,
} from './commonTableColumn';
import React from "react"

test("optionalCellScientificFormatter handles empty string", () => {
  const actual = optionalCellScientificFormatter({ value : "" })
  const expected = ""
  expect(actual).toBe(expected)
});

test("optionalCellScientificFormatter handles numbers", () => {
  const actual = optionalCellScientificFormatter({ value : "1.0" })
  const expected = "1.0e+0"
  expect(actual).toBe(expected)
});


test("optionaCellNumberFormatter handles empty string", () => {
  const actual = optionalCellNumberFormatter({ value : "" })
  const expected = ""
  expect(actual).toBe(expected)
});

test("optionalCellScientificFormatter handles numbers", () => {
  const actual = optionalCellNumberFormatter({ value : "1.0" })
  const expected = 1
  expect(actual).toBe(expected)
});

test("optionalCellDecimalFormatter handles empty string", () => {
  const actual = optionalCellDecimalFormatter({ value : "" })
  const expected = ""
  expect(actual).toBe(expected)
});

test("optionalCellDecimalFormatter handles numbers", () => {
  const actual = optionalCellDecimalFormatter({ value : "1.0" })
  const expected = "1.00"
  expect(actual).toBe(expected)
});

test("null filterDownload", () => {
  const actual = filterDownload(null)
  expect(actual).toBe(true)
});

test("false filterDownload", () => {
  const actual = filterDownload({ accessor : "test" , download : false})
  expect(actual).toBe(false)
});

test("true filterDownload", () => {
  const actual = filterDownload({ accessor : "test", download : true})
  expect(actual).toBe(true)
});

test("implicit CSV Link Header", () => {
  const actual = createCSVLinkHeaders([{ accessor : "test" }])
  expect(actual).toStrictEqual([{"key": "test", "label": "test"}])
});

test("create CSV Link Header", () => {
  const actual = createCSVLinkHeaders([{download : true, accessor : "test" }])
  expect(actual).toStrictEqual([{"key": "test", "label": "test"}])
});

test("skip CSV Link Header", () => {
  const actual = createCSVLinkHeaders([{download : false, accessor : "test" }])
  expect(actual).toStrictEqual([])
});

test("pValueCellFormatterSentinel", () => {
  const actual = pValueCellFormatter({ value : pValueSentinel});
  expect(actual).toBe(" << 5e-324")
});

test("pValueCellFormatter1", () => {
  const actual = pValueCellFormatter({ value : 1});
  const expected = "1.0e+0";
  expect(actual).toBe(expected);
});

test("pValueCellFormatter1text", () => {
  const actual = pValueCellFormatter({ value : 1});
  const expected = "1.0e+0";
  expect(actual).toBe(expected);
});

test("pValueCellFormatterNull", () => {
  const actual = pValueCellFormatter({ value : null});
  expect(actual).toBeNull()
});

test("addHeader empty", () => {
  const actual = addHeader({})
  const expected  = {}
  expect(actual).toStrictEqual(expected)
})

test("addHeader empty title", () => {
  const actual = addHeader({ title: 'title'}, (title : string | null, label : string| null) => <span>{title}</span>)
  const expected  = {"Header": <span>title</span> }
  expect(actual).toStrictEqual(expected)
})


test("nearest gene formatter : null", () => {
  const actual = nearestGeneFormatter(null);
  const expected = <></>;
  expect(actual).toStrictEqual(expected);
    })

test("nearest gene formatter : undefined", () => {
  const actual = nearestGeneFormatter(null);
  const expected = <></>;
  expect(actual).toStrictEqual(expected);
})

test("nearest gene formatter : undefined", () => {
  const actual = nearestGeneFormatter("APOE");
  const expected = [<a key={"APOE"} href="/gene/APOE">APOE</a>];
  expect(actual).toStrictEqual(expected);
})


test("nearest gene formatter : undefined", () => {
  const actual = nearestGeneFormatter("APOE,MAP3K14");
  const expected = [
    <a key={"APOE"} href="/gene/APOE">APOE</a> ,
    <span key={"1"}> , </span> ,
    <a key={"MAP3K14"} href="/gene/MAP3K14">MAP3K14</a> ,];
  expect(actual).toStrictEqual(expected);
})

test("check risteys link formatter : risteysLinkFormatter", () => {
    const actual = risteysLinkFormatter("T2D");
  const expected = <a href="T2D" style={{
    "backgroundColor": "#2779bd",
    "borderRadius": ".25rem",
    "boxShadow": "0 0 5px rgba(0,0,0,.5)",
    "color": "#fff",
    "fontSize": "1.25rem",
    "fontWeight": 700,
    "padding": ".25rem .5rem"
  }}>RISTEYS</a>;
  expect(actual).toStrictEqual(expected);
});

test("risteys link cell : risteysLinkCell", () => {
  const parameters = [
    { "value" : "T2D"},
    { "value" : "T2D", "row" : { "hasRisteys" : true } },
    { "value" : "T2D", "row" : { "hasRisteys" : false } },
    { "value" : "T2D", "row" : { "risteysPhenocode" : "AB1TUBERCU_MILIARY" } },
    { "row" : { "risteysPhenocode" : "AB1TUBERCU_MILIARY" } },
    { "value" : "T2D", "row" : { "risteysURLPrefix" : "http://localhost/" } },
    { "value" : "T2D", "row" : { "risteysURL" : "http://localhost/T2D" } },


  ]
  const actual = parameters.map(risteysURLFormatter);
  const expected = [
    "https://risteys.finregistry.fi/phenocode/T2D",
    "https://risteys.finregistry.fi/phenocode/T2D",
    null,
    "https://risteys.finregistry.fi/phenocode/AB1TUBERCU_MILIARY",
    "https://risteys.finregistry.fi/phenocode/AB1TUBERCU_MILIARY",
    "http://localhost/T2D",
    "http://localhost/T2D",
  ];
  expect(actual).toStrictEqual(expected);
});

test("risteys link cell : risteysLinkCell", () => {
  const parameters = [
    { "value" : "T2D"},
  ]
  const actual = parameters.map(risteysLinkCell);
  const expected = [
    <a href="https://risteys.finregistry.fi/phenocode/T2D" style={{
      "backgroundColor": "#2779bd",
      "borderRadius": ".25rem",
      "boxShadow": "0 0 5px rgba(0,0,0,.5)",
      "color": "#fff",
      "fontSize": "1.25rem",
      "fontWeight": 700,
      "padding": ".25rem .5rem"
    }}>RISTEYS</a>] ;
  expect(actual).toStrictEqual(expected);
});
