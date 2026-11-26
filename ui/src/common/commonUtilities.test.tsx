/* eslint-env jest */
// https://stackoverflow.com/questions/59833839/swap-one-typescript-type-with-another-inside-an-object
import {
    defaultEmptyArray,
    compose,
    flatten,
    get,
    mustacheDiv,
    mustacheSpan,
    mustacheText,
    isNonEmptyArray,
    capitalizeFirstLetter
} from './commonUtilities';
import { render } from "@testing-library/react";
import { variantToPheweb } from './commonModel';


test("capitalizeFirstLetter", () => {
    expect(capitalizeFirstLetter("hello")).toBe("Hello")
    expect(capitalizeFirstLetter("world")).toBe("World")
    expect(capitalizeFirstLetter("")).toBe("")
    expect(capitalizeFirstLetter(null)).toBe("")
    expect(capitalizeFirstLetter("test")).toBe("test")
});


test("get search results : trivial", () => {
  expect(
    compose(
      (x: number) => x * 2,
      (y: number) => y * 3
    )(5)
  ).toBe(30);
});

test("get", async () => {
  const response: Response = {
    json: () => Promise.resolve({ key: "1" }),
  } as Response;
  const handler = jest.fn((x) => {});
  const fetchURL: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response> = (input: RequestInfo, init?: RequestInit) => Promise.resolve(response);
  global.fetch = jest.fn(fetchURL) as unknown as (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  get("url", handler, (url : string) => (e : Error) => {}).then(() => expect(handler.mock.calls.length).toBe(0));
});

test("mustacheDiv", () => {
  const uuid = crypto.randomUUID();
  const wrapper = render(mustacheDiv("<i>{{uuid}}</i>", { uuid }));
  expect(wrapper.container.textContent).toContain(uuid);
});

test("mustacheDiv 23", () => {
    const number23 = render(mustacheDiv("{{23toX chr}}", { "chr" : 23 }));
    expect(number23.container.textContent).toBe("X");
    const text23 = render(mustacheDiv("{{23toX chr}}", { "chr" : "23" }));
    expect(text23.container.textContent).toBe("X");
    const text24 = render(mustacheDiv("{{23toX chr}}", { "chr" : "24" }));
    expect(text24.container.textContent).toBe("24");
});

test("mustacheDiv isX", () => {
    const uuid = crypto.randomUUID();
    const isX1 = render(mustacheDiv("{{#unless (isX chr)}}{{ uuid }}{{/unless}}", { "chr" : "23" , "uuid" : uuid }));
    expect(isX1.container.textContent).toBe("");
    const isX2 = render(mustacheDiv("{{#unless (isX chr)}}{{ uuid }}{{/unless}}", { "chr" : 23  , "uuid" : uuid}));
    expect(isX2.container.textContent).toBe("");
    const isX3 = render(mustacheDiv("{{#unless (isX chr)}}{{ uuid }}{{/unless}}", { "chr" : "X"  , "uuid" : uuid }));
    expect(isX3.container.textContent).toBe("");
    const isX4 = render(mustacheDiv("{{#unless (isX chr)}}{{ uuid }}{{/unless}}", { "chr" : 24  , "uuid" : uuid }));
    expect(isX4.container.textContent).toBe(uuid);
})

test("mustacheSpan", () => {
  const uuid = crypto.randomUUID();
  const wrapper = render(mustacheSpan("<i>{{uuid}}</i>", { uuid }));
  expect(wrapper.container.textContent).toContain(uuid);
});

test("mustacheText", () => {
  const uuid = crypto.randomUUID();
  expect(mustacheText("{{uuid}}", { uuid })).toContain(uuid);
});



test("flatten empty", () => {
  expect(flatten<number>([])).toStrictEqual([]);
});

test("flatten singleton", () => {
  const uuid = crypto.randomUUID();
  expect(flatten<string>([[uuid]])).toStrictEqual([uuid]);
});

test("flatten list flattens", () => {
  const uuid1 = crypto.randomUUID();
  const uuid2 = crypto.randomUUID();
  expect(flatten<string>([[uuid1],[uuid2]])).toStrictEqual([uuid1,uuid2]);
});


test("default empty array defaults", () => {
  const uuid1 = crypto.randomUUID();
  expect(defaultEmptyArray([],[uuid1])).toStrictEqual([uuid1]);
});

test("default empty array does not default", () => {
  const uuid1 = crypto.randomUUID();
  const uuid2 = crypto.randomUUID();
  expect(defaultEmptyArray([uuid1],[uuid2])).toStrictEqual([uuid1]);
});

test("test isNonEmptyArray", () => {
    expect(isNonEmptyArray(null)).toBe(false);
    expect(isNonEmptyArray(undefined)).toBe(false);
    expect(isNonEmptyArray(1)).toBe(false);
    expect(isNonEmptyArray([])).toBe(false);
    expect(isNonEmptyArray([1, 2, 3])).toBe(true);
});